#!/usr/bin/env python3
"""Fetch stock B-roll originals (Pexels, Wikimedia Commons) into a project's broll/ folder with a manifest the edit reads.

    broll_fetch.py search <words> [--n 12]                      Wikimedia Commons video ids (keyless; CC0 / PD / CC BY only)
    broll_fetch.py search <words> --pexels [--n 12] [--any]     Pexels video ids from the API (portrait first; needs PEXELS_API_KEY)
    broll_fetch.py photos <words> --dir $P/broll [--n 4] [--any] [--beat NAME]
                                                                Pexels photos (portrait, original size) + manifest rows "kind": "photo"
    broll_fetch.py get <url|id> [...] --dir $P/broll [--beat NAME] [--min 1080]
                                                                download the ORIGINAL, probe it, 3 look frames, manifest row
    broll_fetch.py note <id|file> --dir $P/broll [--desc TEXT] [--in S] [--out S] [--beat NAME]
                                                                after looking at the frames: what it shows, the usable window
    broll_fetch.py list --dir $P/broll                          the manifest as a table; rows still missing desc/in/out

Sources (`get` needs no API key for either; `search --pexels` reads PEXELS_API_KEY from the environment or the skill's
.env / .env.local, free at pexels.com/api, and searches Wikimedia Commons when there is no key):
- Pexels: a video page URL (https://www.pexels.com/video/<slug>-<id>/), its id, or "pexels:<id>". The original comes from
  the public download link https://www.pexels.com/download/video/<id>/ (a redirect to the uploaded file, often 4K).
  Pexels search pages and the API need a browser or a key, so find clips with a web search for
  "site:pexels.com/video <what the line shows>" and pass the result URLs here. Pexels License: free, no attribution.
- Wikimedia Commons: "commons:<pageid>" from `search`. Only files whose own page shows CC0, public domain or CC BY are
  fetched (CC BY rows carry a "credit" line for the post caption); CC BY-SA and the rest are refused.

Manifest: <dir>/manifest.json, a list of rows (one per clip; `get` on an existing id refreshes the probe, keeps the notes):
  {"id": "p5852479", "source": "pexels", "page": "<page url>", "pexels_url" | "commons_url": "<page url>",
   "file": "broll/p5852479.mp4",              # relative to the project (the parent of --dir)
   "w": 2160, "h": 4096, "fps": 25.0, "duration": 5.08, "hdr": false,
   "full_screen_ok": true,                    # a 9:16 crop is at least 1080 px wide (no upscaling at 1080x1920)
   "frames": ["broll/p5852479_a.jpg", "_b", "_c"],   # 15 %, 50 %, 85 % of the clip, 360 px wide: look before using it
   "beat": "sleep", "desc": "", "best_in": null, "best_out": null,   # filled by `note` after looking at the frames
   "licence": "Pexels License", "fetched": "2026-10-14"}
Then every insert goes through insert_prep.py (cut, people and line check, SDR, fps conform, grade onto the speaker's
plate): `insert_prep.py <file> <out> --in <best_in> --dur <s> --ref assets/plate.mp4`. Stock is the last source in
talking-head styles (references/broll.md 3): own footage first, then stills, then stock video inside a frame.
"""
import argparse, datetime, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
LICENCE = {"pexels": "Pexels License"}
# Keyless fallback (11-12): Wikimedia Commons videos whose own file page says CC0, public domain or CC BY (credit kept in the
# manifest row for the post caption). CC BY-SA is refused: share-alike could reach the buyer's whole reel. Mixkit is gone: its
# User Terms forbid fetching Items by script, which a sold TadClip can't do.
COMMONS_OK = re.compile(r"^(cc0|cc-zero|public domain|pd|pd-[a-z0-9-]+|cc by [0-9.]+|cc-by-[0-9.]+)$", re.I)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
X264_THREADS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "X264_THREADS")).read().strip()   # pinned like every encode (doctor.sh)


def http(url, method="GET"):
    return urllib.request.urlopen(urllib.request.Request(url, method=method, headers={"User-Agent": UA}), timeout=60)


def parse(ref):
    """url | id | pexels:<id> | commons:<pageid> -> (source, numeric id, page url or None)"""
    ref = ref.strip()
    m = re.match(r"(pexels|commons):(\d+)$", ref)
    if m:
        return m.group(1), m.group(2), None
    if re.match(r"\d+$", ref):
        return "pexels", ref, None
    m = re.search(r"pexels\.com/(?:[a-z-]+/)?video/(?:[^/]*?-)?(\d+)/?", ref) or re.search(r"videos\.pexels\.com/video-files/(\d+)/", ref)
    if m:
        return "pexels", m.group(1), ref if "/video/" in ref and "video-files" not in ref else None
    if "mixkit" in ref:
        sys.exit(f"{ref}: Mixkit clips are no longer fetched (its User Terms forbid scripted downloads). Use Pexels or commons:<id>")
    sys.exit(f"not a Pexels or Wikimedia Commons clip: {ref}")


def commons_info(pageid):
    q = urllib.parse.urlencode({"action": "query", "pageids": pageid, "prop": "imageinfo", "iiprop": "url|size|mediatype|extmetadata", "format": "json"})
    page = json.load(http(f"{COMMONS_API}?{q}"))["query"]["pages"][str(pageid)]
    ii = page["imageinfo"][0]; md = ii.get("extmetadata", {})
    val = lambda k: re.sub(r"<[^>]+>", "", (md.get(k) or {}).get("value", "")).strip()
    return {"title": page["title"], "url": ii["url"], "page": ii.get("descriptionurl"), "w": ii.get("width"), "h": ii.get("height"),
            "licence": val("LicenseShortName"), "artist": val("Artist"), "credit": val("Credit"), "attribution": val("AttributionRequired")}


def original_url(src, vid):
    """the largest original file; Commons: the original, only when its file page shows an allowed licence"""
    if src == "pexels":
        r = http(f"https://www.pexels.com/download/video/{vid}/", "HEAD")
        return r.geturl()
    info = commons_info(vid)
    return info["url"] if COMMONS_OK.match(info["licence"]) else None


def download(url, dest):
    head = http(url, "HEAD")
    size = int(head.headers.get("Content-Length") or 0)
    if os.path.exists(dest) and size and os.path.getsize(dest) == size:
        return size, False
    tmp = dest + ".part"
    with http(url) as r, open(tmp, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    if size and os.path.getsize(tmp) != size:
        os.remove(tmp)
        raise OSError(f"download incomplete: {url}")
    os.replace(tmp, dest)
    return os.path.getsize(dest), True


def fetch(url, dest):
    """One retry: Pexels answers a passing 403 to a file that downloads fine a moment later (2026-11-05)."""
    try:
        return download(url, dest)
    except OSError:  # URLError and HTTPError are OSErrors
        time.sleep(3)
        return download(url, dest)


def probe(f):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate,avg_frame_rate,color_transfer"
                                   ":stream_side_data=rotation,side_data_type,crop_left,crop_right,crop_top,crop_bottom:format=duration",
                                   "-of", "json", f], capture_output=True, text=True, check=True).stdout)
    s = j["streams"][0]
    w, h = s["width"], s["height"]
    sds = s.get("side_data_list", []) or []
    for d in sds:                       # the size ffmpeg decodes: container crop off first (grade_lib.shown_size), then upright
        if d.get("side_data_type") == "Frame Cropping":
            w -= int(d.get("crop_left", 0) or 0) + int(d.get("crop_right", 0) or 0)
            h -= int(d.get("crop_top", 0) or 0) + int(d.get("crop_bottom", 0) or 0)
    rot = next((abs(int(d.get("rotation", 0))) for d in sds if "rotation" in d), 0)
    if rot in (90, 270):
        w, h = h, w
    n, d = (s.get("avg_frame_rate") or s["r_frame_rate"]).split("/")
    fps = round(float(n) / float(d), 3) if float(d) else 0.0
    return {"w": w, "h": h, "fps": fps, "duration": round(float(j["format"]["duration"]), 3),
            "hdr": s.get("color_transfer") in ("arib-std-b67", "smpte2084"),
            "full_screen_ok": min(w, round(h * 9 / 16)) >= 1080}


def look_frames(f, stem, dur):
    out = []
    for tag, q in (("a", 0.15), ("b", 0.5), ("c", 0.85)):
        jpg = f"{stem}_{tag}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * q:.3f}", "-i", f, "-frames:v", "1", "-vf", "scale=360:-2",
                        "-q:v", "4", jpg], check=True)
        out.append(jpg)
    return out


def load(d):
    p = os.path.join(d, "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else []


def save(d, rows):
    json.dump(rows, open(os.path.join(d, "manifest.json"), "w"), ensure_ascii=False, indent=1)


def find(rows, ref):
    """a row by id (p123 / m456), bare number, or file name; rows from older manifests have no id, only a file"""
    k = os.path.splitext(os.path.basename(ref))[0]
    keys = {k, "p" + k, "m" + k}
    for r in rows:
        if keys & {r.get("id"), os.path.splitext(os.path.basename(r.get("file", "")))[0]}:
            return r
    return None


def cmd_get(A):
    d = os.path.abspath(A.dir); os.makedirs(d, exist_ok=True)
    proj = os.path.dirname(d)
    rel = lambda p: os.path.relpath(p, proj)
    rows = load(d); bad = 0
    for ref in A.refs:
        src, vid, page = parse(ref)
        rid = ("p" if src == "pexels" else "c") + vid
        f = os.path.join(d, rid + ".mp4")
        try:
            url = original_url(src, vid)
            if not url:
                print(f"{rid}: its Commons licence is not CC0, public domain or CC BY: skipped"); bad += 1; continue
            if src == "commons":   # Commons keeps Ogg Theora/WebM: H.264 so the renderer's Chrome can play it (it dropped Theora)
                raw = f + ".src"; size, fresh = fetch(url, raw)
                if fresh or not os.path.exists(f):
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-an", "-c:v", "libx264", "-threads", X264_THREADS, "-crf", "16", "-preset", "medium",
                                    "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", f], check=True)
                    os.remove(raw)
            else:
                size, fresh = fetch(url, f)
        except (OSError, subprocess.CalledProcessError) as e:  # one bad clip must not end the batch
            print(f"{rid}: download failed ({e}): skipped"); bad += 1; continue
        info = probe(f)
        if min(info["w"], info["h"]) < A.min:
            print(f"{rid}: {info['w']}x{info['h']} is below --min {A.min}: removed"); os.remove(f); bad += 1; continue
        frames = look_frames(f, os.path.join(d, rid), info["duration"])
        row = find(rows, rid)
        if row is None:
            row = {"id": rid, "beat": A.beat or "", "desc": "", "best_in": None, "best_out": None}
            rows.append(row)
        elif A.beat:
            row["beat"] = A.beat
        lic = LICENCE.get(src)
        if src == "commons":
            ci = commons_info(vid); page = page or ci["page"]; lic = f"{ci['licence']} (Wikimedia Commons)"
            if re.match(r"cc[ -]by", ci["licence"], re.I):   # CC BY: the credit goes in the post caption
                row["credit"] = f"{ci['title'].removeprefix('File:')} by {ci['artist'] or ci['credit'] or 'see page'}, {ci['licence']}, via Wikimedia Commons"
        page = page or row.get("page") or f"https://www.pexels.com/video/{vid}/"
        row.update({"source": src, "page": page, f"{src}_url": page, "original": url, "file": rel(f), **info,
                    "frames": [rel(x) for x in frames], "licence": lic, "fetched": datetime.date.today().isoformat()})
        save(d, rows)
        note = "" if info["full_screen_ok"] else "  (a 9:16 crop is under 1080 wide: framed inserts only)"
        print(f"{rid}: {info['w']}x{info['h']} {info['fps']:g} fps {info['duration']:.1f} s{' HDR' if info['hdr'] else ''}, "
              f"{size / 1e6:.0f} MB {'downloaded' if fresh else 'already here'} -> {rel(f)}{note}")
    print(f"manifest: {os.path.join(d, 'manifest.json')} ({len(rows)} clips). Look at the _a/_b/_c frames, then `note` each one.")
    sys.exit(1 if bad and bad == len(A.refs) else 0)


def cmd_note(A):
    d = os.path.abspath(A.dir); rows = load(d)
    row = find(rows, A.ref) or sys.exit(f"{A.ref} is not in {d}/manifest.json")
    for k, v in (("desc", A.desc), ("best_in", A.in_), ("best_out", A.out), ("beat", A.beat)):
        if v is not None:
            row[k] = v
    if row.get("best_in") is not None and row.get("best_out") is not None:
        if not 0 <= row["best_in"] < row["best_out"] <= row.get("duration", 1e9) + 0.01:
            sys.exit(f"window {row['best_in']}-{row['best_out']} is outside the clip (0-{row.get('duration')})")
    save(d, rows)
    print(json.dumps(row, ensure_ascii=False, indent=1))


def cmd_list(A):
    d = os.path.abspath(A.dir); rows = load(d)
    for r in rows:
        todo = [k for k in ("desc", "best_in", "best_out") if r.get(k) in (None, "")]
        win = f"{r['best_in']:.1f}-{r['best_out']:.1f}" if r.get("best_in") is not None and r.get("best_out") is not None else "?"
        print(f"{r.get('id', '?'):>11} {r.get('beat') or '':>10} {r.get('w')}x{r.get('h')} {r.get('fps') or 0:g}fps {r.get('duration') or 0:5.1f}s "
              f"win {win:>9}  {(r.get('desc') or '')[:70]}{'  TODO ' + ','.join(todo) if todo else ''}")
    print(f"{len(rows)} clips in {d}/manifest.json")


def env_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for f in (".env", ".env.local"):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", f)
        m = os.path.exists(p) and re.search(rf"^{name}[ \t]*=[ \t]*['\"]?([^'\"\n]+)", open(p).read(), re.M)
        if m:
            return m.group(1).strip()
    sys.exit(f"no {name}: export it or add it to the skill's .env (keyless: `search` without --pexels for videos, wikimedia_fetch.py for photos)")


def cmd_search_pexels(A):
    try:
        key = env_key("PEXELS_API_KEY")
    except SystemExit:
        print("no PEXELS_API_KEY: searching Wikimedia Commons, which needs no key")
        A.pexels = False
        return cmd_search(A)
    q = urllib.parse.urlencode({"query": " ".join(A.words), "per_page": A.n, "size": "large", **({} if A.any else {"orientation": "portrait"})})
    req = urllib.request.Request(f"https://api.pexels.com/videos/search?{q}", headers={"Authorization": key, "User-Agent": UA})
    j = json.load(urllib.request.urlopen(req, timeout=60))
    for v in j["videos"]:
        print(f"pexels:{v['id']:<9} {v['width']}x{v['height']:<5} {v['duration']:>3} s  {v['url']}")
    print(f"{j['total_results']} Pexels results for {' '.join(A.words)!r} (shown {len(j['videos'])}); pass the ids to `get`, look at the frames")


def cmd_photos(A):
    q = urllib.parse.urlencode({"query": " ".join(A.words), "per_page": A.n, "size": "large", **({} if A.any else {"orientation": "portrait"})})
    req = urllib.request.Request(f"https://api.pexels.com/v1/search?{q}", headers={"Authorization": env_key("PEXELS_API_KEY"), "User-Agent": UA})
    os.makedirs(A.dir, exist_ok=True)
    rows = load(A.dir)
    for ph in json.load(urllib.request.urlopen(req, timeout=60))["photos"]:
        name = f"ph{ph['id']}.jpg"
        download(ph["src"]["original"] + "?auto=compress&cs=tinysrgb&h=2400", os.path.join(A.dir, name))
        rel = f"{os.path.basename(os.path.normpath(A.dir))}/{name}"
        rows = [r for r in rows if r["id"] != f"ph{ph['id']}"] + [{"id": f"ph{ph['id']}", "kind": "photo", "source": "pexels", "page": ph["url"],
                "file": rel, "w": ph["width"], "h": ph["height"], "alt": ph.get("alt", ""), "beat": A.beat, "desc": "",
                "licence": LICENCE["pexels"], "fetched": datetime.date.today().isoformat()}]
        print(f"ph{ph['id']:<10} {ph['width']}x{ph['height']}  {rel}  {ph.get('alt', '')[:70]}")
    save(A.dir, rows)


def cmd_search(A):
    if A.pexels:
        return cmd_search_pexels(A)
    q = urllib.parse.urlencode({"action": "query", "generator": "search", "gsrsearch": "filetype:video " + " ".join(A.words), "gsrnamespace": 6,
                                "gsrlimit": min(50, A.n * 4), "prop": "imageinfo", "iiprop": "size|extmetadata", "format": "json"})
    pages = (json.load(http(f"{COMMONS_API}?{q}")).get("query") or {}).get("pages", {})
    shown = skipped = 0
    for pid, pg in sorted(pages.items(), key=lambda kv: kv[1].get("index", 0)):
        ii = (pg.get("imageinfo") or [{}])[0]; lic = re.sub(r"<[^>]+>", "", (ii.get("extmetadata", {}).get("LicenseShortName") or {}).get("value", "")).strip()
        if not COMMONS_OK.match(lic):
            skipped += 1; continue
        if shown < A.n:
            print(f"commons:{pid:<9} {ii.get('width')}x{ii.get('height'):<5} {lic:<14} {pg['title'][5:][:70]}"); shown += 1
    print(f"{len(pages)} Commons videos for {' '.join(A.words)!r}: shown {shown} with CC0 / public domain / CC BY, {skipped} other licences skipped."
          " Fewer and smaller than Pexels: a free PEXELS_API_KEY in .env gives far more.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="Commons video ids (keyless) or Pexels ids (--pexels)"); s.add_argument("words", nargs="+"); s.add_argument("--n", type=int, default=12)
    s.add_argument("--pexels", action="store_true", help="search the Pexels API instead of Wikimedia Commons"); s.add_argument("--any", action="store_true", help="Pexels: any orientation")
    g = sub.add_parser("get", help="download originals + manifest rows"); g.add_argument("refs", nargs="+"); g.add_argument("--dir", required=True)
    g.add_argument("--beat"); g.add_argument("--min", type=int, default=1080, help="smallest short side kept (px; default 1080, no 720p)")
    n = sub.add_parser("note", help="desc and best window after looking"); n.add_argument("ref"); n.add_argument("--dir", required=True)
    n.add_argument("--desc"); n.add_argument("--in", dest="in_", type=float); n.add_argument("--out", type=float); n.add_argument("--beat")
    ph = sub.add_parser("photos", help="Pexels photos into --dir"); ph.add_argument("words", nargs="+"); ph.add_argument("--dir", required=True)
    ph.add_argument("--n", type=int, default=4); ph.add_argument("--any", action="store_true"); ph.add_argument("--beat")
    li = sub.add_parser("list", help="the manifest as a table"); li.add_argument("--dir", required=True)
    A = ap.parse_args()
    {"search": cmd_search, "photos": cmd_photos, "get": cmd_get, "note": cmd_note, "list": cmd_list}[A.cmd](A)


if __name__ == "__main__":
    main()
