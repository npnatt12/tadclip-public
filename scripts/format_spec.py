#!/usr/bin/env python3
"""Measure a reel's format: numbers, not impressions (docs/format-engine/). The reader agent interprets these.

    format_spec.py <video> [--out spec.json] [--sheet sheet.jpg] [--fps 2]

What it measures (all from the file itself; macOS for the text):
  cuts    hard cuts AND jump cuts (a talking head cut on the same shot: a spike in frame difference against its own
          neighbourhood, not a fixed scene threshold), shot lengths, cuts per minute, the first cut
  text    on-screen text from macOS Vision at --fps: each text event (same words on consecutive samples) with its time,
          position and line height in % of the frame, the zone relative to the face (above / face / chest / lower),
          the colour of the plate behind it and of its letters
  face    how often a face is on screen, where (top/bottom/centre in % of the frame), how big
  audio   integrated loudness (LUFS), quiet share and pauses (ffmpeg silencedetect at -35 dB, 0.35 s)
  sheet   one contact sheet: a frame per shot, its start time under it
Only ffmpeg, numpy, Pillow, OpenCV (YuNet via face_track.py's model) and macOS Vision: all already in TadClip.
"""
import argparse, json, os, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def probe(v):
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                                     "-of", "json", v], capture_output=True, text=True).stdout)
    s = out["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return float(out["format"]["duration"]), s["width"], s["height"], float(n) / float(d)


def gray_frames(v, fps, w=72, h=128):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def cuts(v, fps, band=None):
    """a cut = a frame whose difference from the previous one is a local peak, at least 3.5x the median of its +-0.5 s
    neighbourhood and above an absolute floor (so grain and a moving hand don't count). Jump cuts in a talking head are
    small but sudden: the ratio catches them where a scene threshold doesn't."""
    f = gray_frames(v, fps)
    dd = np.abs(np.diff(f, axis=0)); d = dd.mean(axis=(1, 2))
    # the face band (rows where the speaker's face sits) on its own: a cut there is a cut of the speaker's shot; a spike
    # only outside it is an insert, a panel or a screen recording changing while the speaker keeps talking (11-10: a
    # creator's 45 s reel had 10 frame cuts but 3 shots of the speaker)
    if band:   # band = the median face box (top, bottom, left, right in % of the frame)
        H_, W_ = f.shape[1], f.shape[2]
        r0, r1 = int(band[0] * H_ / 100), max(int(band[0] * H_ / 100) + 2, int(band[1] * H_ / 100))
        c0, c1 = max(0, int(band[2] * W_ / 100)), min(W_, max(int(band[2] * W_ / 100) + 2, int(band[3] * W_ / 100)))
        fb = dd[:, r0:r1, c0:c1].mean(axis=(1, 2))
    else: fb = d
    k = max(3, int(fps / 2)); out = []
    for i in range(1, len(d) - 1):
        lo, hi = max(0, i - k), min(len(d), i + k + 1)
        around = np.delete(d[lo:hi], i - lo)
        if d[i] >= d[i - 1] and d[i] >= d[i + 1] and d[i] > 4.0 and d[i] > 3.5 * max(np.median(around), 0.5):
            t = round((i + 1) / fps, 3)
            fa = np.delete(fb[lo:hi], i - lo)
            kind = "shot" if fb[i] > 4.0 * max(np.median(fa), 0.3) and fb[i] > 4.0 else "insert"   # 11-10: real jump cuts x7-x90, a panel change x1.7
            if not out or t - out[-1][0] > 0.25: out.append((t, kind))
    return out


def ocr(paths):   # macOS Vision or Windows OCR (scripts/ocr.py)
    sys.path.insert(0, HERE); import ocr as _ocr
    by = (_ocr.lines(paths, "th-TH,en-US") if paths else None) or {}
    return [by.get(p, {"lines": []}) for p in paths]


def faces(frames_dir, names):
    """YuNet on the sampled frames: [(top, bottom, cx, height) in % of the frame] or None per frame"""
    try:
        import cv2
        from face_track import MODEL, MODEL_URL
        if not os.path.exists(MODEL):
            import urllib.request; os.makedirs(os.path.dirname(MODEL), exist_ok=True); urllib.request.urlretrieve(MODEL_URL, MODEL)
    except Exception: return [None] * len(names)
    det = None; out = []
    for n in names:
        im = cv2.imread(os.path.join(frames_dir, n)); h, w = im.shape[:2]
        if det is None: det = cv2.FaceDetectorYN.create(MODEL, "", (w, h), 0.7)
        _, fs = det.detect(im)
        if fs is None or not len(fs): out.append(None); continue
        x, y, fw, fh = max(fs, key=lambda f: f[2] * f[3])[:4]
        out.append((100 * y / h, 100 * (y + fh) / h, 100 * (x + fw / 2) / w, 100 * fh / h))
    return out


def colours(img, box):
    """(plate, letters) of a text box. The plate is the colour of a thin ring just inside the box edge when that ring is
    one flat colour (a card, a block); otherwise the text sits on footage: plate None. The letters are the most common
    colour inside the box that is far from the plate (or from the ring's median)."""
    x, y, w, h = [int(v) for v in box]; a = np.asarray(img.convert("RGB")).astype(int)
    x0, y0, x1, y1 = max(0, x - 2), max(0, y - 2), min(a.shape[1], x + w + 2), min(a.shape[0], y + h + 2)
    reg = a[y0:y1, x0:x1]; r = max(2, (y1 - y0) // 10)
    ring = np.concatenate([reg[:r].reshape(-1, 3), reg[-r:].reshape(-1, 3), reg[:, :r].reshape(-1, 3), reg[:, -r:].reshape(-1, 3)])
    med = np.median(ring, 0); flat = (np.abs(ring - med).sum(1) < 40).mean() > 0.8
    q = reg.reshape(-1, 3) // 16; vals, n = np.unique(q, axis=0, return_counts=True)
    far = next((vals[i] * 16 + 8 for i in np.argsort(-n) if np.abs(vals[i] * 16 + 8 - med).sum() > 120), None)
    hx = lambda c: "#" + "".join(f"{int(min(255, v)):02X}" for v in c)
    return (hx(med) if flat else None), (hx(far) if far is not None else None)


def loudness(v):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    s = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-af", "silencedetect=n=-35dB:d=0.35", "-f", "null", "-"], capture_output=True, text=True).stderr
    q = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", s)]
    return (float(m[-1]) if m else None), q


def measure(v, fps=2.0, sheet=None):
    dur, W, H, vfps = probe(v)
    tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={fps}", "-q:v", "3", os.path.join(tmp, "f%05d.jpg")], check=True)
    names = sorted(os.listdir(tmp)); times = [i / fps for i in range(len(names))]
    texts = ocr([os.path.join(tmp, n) for n in names]); fc = faces(tmp, names)
    fs = [f for f in fc if f]
    # the face box in % of the frame: f = (top, bottom, cx, height); the face's width ~ 0.8 of its height in pixels
    band = None
    if fs:
        top, bot, cx, hh = (float(np.median([f[k] for f in fs])) for k in range(4)); half = 0.4 * hh * H / W
        band = (top, bot, cx - half, cx + half)
    ck = cuts(v, min(vfps, 30), band); cs = [t for t, _ in ck]; shot_cuts = [t for t, k in ck if k == "shot"]
    shots = np.diff([0.0] + shot_cuts + [dur])
    # text: track each line across samples (OCR wobbles: similar words at the same place are one line), keep lines seen
    # on 2+ samples (popups last 1 s or more; footage textures read as noise change every frame), set aside lines on
    # screen most of the reel (chrome: a logo, a tagline), then group lines shown together and stacked into one card
    from difflib import SequenceMatcher
    tracks = []
    for t, n, o, f in zip(times, names, texts, fc):
        Wi, Hi = o.get("w") or W, o.get("h") or H; Wi, Hi = float(Wi), float(Hi)
        for l in o.get("lines", []):
            txt = l["text"].strip()
            if len(re.sub(r"\W", "", txt)) < 2: continue
            x, y, w, h = l["box"]; cx, cy = 100 * (x + w / 2) / Wi, 100 * (y + h / 2) / Hi
            tr = next((r for r in tracks if r["last"] >= t - 1.01 / fps and abs(r["cy"] - cy) < 4 and abs(r["cx"] - cx) < 12
                       and SequenceMatcher(None, r["text"], txt).ratio() >= 0.6), None)
            if tr: tr["last"] = t; tr["n"] += 1; tr["hs"].append(100 * h / Hi); tr["texts"].append(txt); continue
            tracks.append({"text": txt, "texts": [txt], "first": t, "last": t, "n": 1, "cx": cx, "cy": cy, "hs": [100 * h / Hi], "frame": n, "box": l["box"], "face": f})
    tracks = [r for r in tracks if r["n"] >= 2]
    for r in tracks: r["text"] = max(set(r["texts"]), key=r["texts"].count); r["dur"] = r["last"] - r["first"] + 1 / fps
    # chrome: the same words at the same place for 40 %+ of the reel in total (a logo, a tagline), even if a full-screen
    # transition interrupts it
    pool = {}
    for r in tracks: pool.setdefault((re.sub(r"\W", "", r["text"].lower()), round(r["cx"] / 8), round(r["cy"] / 8)), []).append(r)
    chrome = [r for g in pool.values() if sum(x["dur"] for x in g) >= 0.4 * dur for r in g]
    rest = sorted((r for r in tracks if r not in chrome), key=lambda r: (r["first"], r["cy"]))
    ev = []
    for r in rest:
        e = next((e for e in ev if abs(e["t0"] - r["first"]) <= 0.6 and min(abs(r["cy"] - y) for y in e["ys"]) < 14), None)
        if e: e["rows"].append(r); e["ys"].append(r["cy"]); e["t1"] = max(e["t1"], r["last"] + 1 / fps); continue
        ev.append({"t0": r["first"], "t1": r["last"] + 1 / fps, "rows": [r], "ys": [r["cy"]]})
    out_ev = []
    for e in ev:
        rows = sorted(e["rows"], key=lambda r: r["cy"]); big = max(rows, key=lambda r: np.median(r["hs"])); f = big["face"]
        cy = float(np.mean([r["cy"] for r in rows]))
        zone = "no-face" if f is None else "above" if cy < f[0] else "face" if cy <= f[1] else "chest" if cy <= f[1] + 25 else "lower"
        cl = [colours(Image.open(os.path.join(tmp, r["frame"])), r["box"]) for r in rows]   # per row: a stair has a block on row 2 only
        plate = sorted({c[0] for c in cl if c[0]}); letters = sorted({c[1] for c in cl if c[1]})
        out_ev.append({"t0": round(e["t0"], 2), "t1": round(e["t1"], 2), "text": " / ".join(r["text"] for r in rows)[:120], "rows": len(rows),
                       "x": round(big["cx"], 1), "y": round(cy, 1), "line_h": round(float(np.median(big["hs"])), 2), "zone": zone, "plate": plate, "letters": letters})
    ev = out_ev
    cover = np.zeros(int(dur * fps) + 2, bool)
    for e in ev: cover[int(e["t0"] * fps):int(e["t1"] * fps)] = True
    on = cover.sum() / fps   # time with any text on screen (events overlap: a union, not a sum)
    seen = [f for f in fc if f]
    lufs, quiet = loudness(v)
    spec = {
        "source": os.path.basename(v), "seconds": round(dur, 2), "w": W, "h": H,
        "cuts": {"n": len(cs), "times": cs, "per_min": round(60 * len(cs) / dur, 1) if dur else None,
                 "shot_cuts": shot_cuts, "shot_cuts_per_min": round(60 * len(shot_cuts) / dur, 1) if dur else None,
                 "insert_changes": [t for t, k in ck if k == "insert"],
                 "shot_median": round(float(np.median(shots)), 2), "shot_p90": round(float(np.percentile(shots, 90)), 2), "first": cs[0] if cs else None},
        "text": {"events": len(ev), "share_of_time": round(on / dur, 3) if dur else 0, "first_seen": ev[0]["t0"] if ev else None,
                 "line_h_median": round(float(np.median([e["line_h"] for e in ev])), 2) if ev else None,
                 "zones": {z: round(sum(e["t1"] - e["t0"] for e in ev if e["zone"] == z) / max(sum(e["t1"] - e["t0"] for e in ev), 1e-6), 2) for z in sorted({e["zone"] for e in ev})},
                 "rows_median": float(np.median([e["rows"] for e in ev])) if ev else None, "seconds_median": round(float(np.median([e["t1"] - e["t0"] for e in ev])), 2) if ev else None,
                 "gap_median": round(float(np.median(np.diff([e["t0"] for e in ev]))), 2) if len(ev) > 1 else None,
                 "chrome": sorted({(r["text"], round(r["cx"]), round(r["cy"])) for r in chrome}),
                 "list": ev},
        "face": {"share": round(len(seen) / max(1, len(fc)), 2), "top": round(float(np.median([f[0] for f in seen])), 1) if seen else None,
                 "bottom": round(float(np.median([f[1] for f in seen])), 1) if seen else None,
                 "cx": round(float(np.median([f[2] for f in seen])), 1) if seen else None, "height": round(float(np.median([f[3] for f in seen])), 1) if seen else None},
        "audio": {"lufs": lufs, "quiet_share": round(sum(quiet) / dur, 3) if dur else None, "pauses_per_min": round(60 * len(quiet) / dur, 1) if dur else None,
                  "longest_pause": round(max(quiet), 2) if quiet else 0},
    }
    if sheet:   # a frame per shot (up to 24), its start time under it
        starts = ([0.0] + cs)[:24]; tiles = []
        for s in starts:
            i = min(len(names) - 1, int(round((s + 0.3) * fps)))
            im = Image.open(os.path.join(tmp, names[i])).convert("RGB"); im.thumbnail((180, 320))
            c = Image.new("RGB", (180, 340), "white"); c.paste(im, ((180 - im.width) // 2, 0)); ImageDraw.Draw(c).text((6, 322), f"{s:.2f}s", fill="black"); tiles.append(c)
        cols = 8; rows = (len(tiles) + cols - 1) // cols; S = Image.new("RGB", (cols * 180, rows * 340), "white")
        for i, c in enumerate(tiles): S.paste(c, ((i % cols) * 180, (i // cols) * 340))
        S.save(sheet, quality=85)
    return spec


def check():
    """self-test: three test patterns joined at 2.0 s and 3.5 s, (testsrc2 moves inside itself: motion, not a cut)"""
    d = tempfile.mkdtemp(); parts = []
    for i, (src, sec) in enumerate([("testsrc2=s=360x640:r=30", 2.0), ("smptebars=s=360x640:r=30", 1.5), ("rgbtestsrc=s=360x640:r=30", 1.5)]):
        p = os.path.join(d, f"p{i}.mp4"); parts.append(p)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}:d={sec}", "-pix_fmt", "yuv420p", p], check=True)
    lst = os.path.join(d, "l.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts)); v = os.path.join(d, "v.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", v], check=True)
    got = cuts(v, 30); ts = [t for t, _ in got]
    ok = len(ts) == 2 and abs(ts[0] - 2.0) <= 0.05 and abs(ts[1] - 3.5) <= 0.05
    print(("ok  " if ok else "FAIL") + f" cuts at 2.0 and 3.5 s, nothing else: {ts}"); return ok


if __name__ == "__main__":
    if "--check" in sys.argv: sys.exit(0 if check() else 1)
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out"); ap.add_argument("--sheet"); ap.add_argument("--fps", type=float, default=2.0)
    a = ap.parse_args()
    s = measure(a.video, a.fps, a.sheet)
    j = json.dumps(s, ensure_ascii=False, indent=1)
    open(a.out, "w").write(j) if a.out else print(j)
    if a.out: print(f"{s['source']}: {s['seconds']} s, {s['cuts']['n']} cuts ({s['cuts']['per_min']}/min, of the speaker's shot {s['cuts']['shot_cuts_per_min']}/min), {s['text']['events']} text events, face {s['face']['share']:.0%}, {s['audio']['lufs']} LUFS")
