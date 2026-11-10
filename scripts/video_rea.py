#!/usr/bin/env python3
"""Video teardown and competitor analysis: measure, draw, and fill the report templates (recipes/rea/README.md).
The agent then writes the reading parts by its brief (docs/format-engine/method/rea, .../competitors).

    video_rea.py teardown <video> [<video> ...] --out DIR
        per video: DIR/<id>/spec.json, sheet.jpg, timeline.png, report.md (the template with the measured parts filled)
    video_rea.py competitors <name>=<video|dir> [<name>=...] --out DIR
        an account = one name with 1+ videos (a dir: every .mp4 in it); measures each reel, then DIR/compare.md (the
        template with the side-by-side table filled), DIR/compare.json, and a teardown folder per reel. The account
        named --owner (default "you") is the user's own and goes last.
    --account NAME   teardown only: the account name in the report (default: the uploader in study.json)

    video_rea.py --check   templates still match this script; pure parts work

Anything the script can't measure is handed to the agent as "[agent: hint]". The hook end is provisional (3 s) until
the agent corrects it; the body numbers are counted from it.

Measures with format_spec.py (macOS for on-screen text). Nothing is downloaded here: creator_study.py fetches."""
import argparse, glob, json, os, re, statistics, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import format_spec
TPL = os.path.join(HERE, "..", "docs", "format-engine", "method", "rea")
ZONE = {"above": (59, 130, 246), "face": (239, 68, 68), "chest": (16, 185, 129), "lower": (234, 179, 8), "no-face": (148, 163, 184)}


def timeline(spec, path, W=1400):
    """one strip per kind: speaker cuts, insert changes, text events by zone (rows stacked when they overlap)"""
    dur = spec["seconds"] or 1; x = lambda t: 60 + int((W - 80) * t / dur)
    ev = spec["text"]["list"]; lanes = []
    for e in ev:
        lane = next((i for i, end in enumerate(lanes) if end <= e["t0"]), None)
        if lane is None: lanes.append(e["t1"]); lane = len(lanes) - 1
        else: lanes[lane] = e["t1"]
        e["_lane"] = lane
    H = 150 + 14 * max(1, len(lanes)); im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    for s in range(0, int(dur) + 1, 5):
        d.line([x(s), 20, x(s), H - 20], fill=(235, 235, 235)); d.text((x(s) - 6, H - 16), f"{s}s", fill=(120, 120, 120))
    d.text((4, 28), "speaker", fill="black"); d.text((4, 58), "inserts", fill="black"); d.text((4, 88), "text", fill="black")
    for t in spec["cuts"].get("shot_cuts", spec["cuts"]["times"]): d.line([x(t), 24, x(t), 46], fill=(17, 17, 17), width=2)
    for t in spec["cuts"].get("insert_changes", []): d.line([x(t), 54, x(t), 76], fill=(124, 58, 237), width=2)
    for e in ev:
        y = 86 + 14 * e["_lane"]; d.rectangle([x(e["t0"]), y, max(x(e["t0"]) + 2, x(e["t1"]) - 1), y + 10], fill=ZONE.get(e["zone"], (0, 0, 0)))
    lx = W - 520
    for i, (z, c) in enumerate(ZONE.items()): d.rectangle([lx + i * 100, 4, lx + i * 100 + 10, 14], fill=c); d.text((lx + i * 100 + 14, 3), z, fill="black")
    im.save(path)


HOOK = 3.0  # ponytail: provisional hook end (the 3 s rule the method cites); the agent corrects it in the report


def body(s, hook=HOOK):
    """speaker cuts after the hook: count, seconds, per minute, median shot (bounded by the hook end and the video end)"""
    cuts = [t for t in s["cuts"].get("shot_cuts", s["cuts"]["times"]) if t > hook]; secs = max(s["seconds"] - hook, 0.01)
    edges = [hook] + cuts + [s["seconds"]]; shots = [b - a for a, b in zip(edges, edges[1:])]
    return {"body_shot_n": len(cuts), "body_seconds": round(secs, 1), "body_shot_per_min": round(len(cuts) * 60 / secs, 1),
            "body_shot_median": round(statistics.median(shots), 2)}


def summary(s):
    """the numbers every report uses, flat"""
    c, t, f, a = s["cuts"], s["text"], s["face"], s["audio"]; mins = (s["seconds"] or 1) / 60
    return {"seconds": s["seconds"], "cuts_per_min": c["per_min"], "speaker_cuts_per_min": c.get("shot_cuts_per_min"),
            "inserts": len(c.get("insert_changes", [])), "insert_per_min": round(len(c.get("insert_changes", [])) / mins, 1),
            "shot_median": c["shot_median"], "shot_p90": c["shot_p90"], "first_cut": c["first"],
            "text_events": t["events"], "text_per_min": round(t["events"] / mins, 1), "text_share": t["share_of_time"], "first_text": t["first_seen"],
            "text_line_h": t["line_h_median"], "text_seconds": t.get("seconds_median"), "text_gap": t.get("gap_median"),
            "text_zone": max(t["zones"], key=t["zones"].get) if t["zones"] else None,
            "chrome": "; ".join(x[0] for x in t.get("chrome", [])) or None, "face_share": f["share"], "face_top": f["top"], "face_bottom": f["bottom"],
            "face_height": f.get("height"), "lufs": a["lufs"], "pauses_per_min": a["pauses_per_min"], "longest_pause": a["longest_pause"], **body(s)}


def fill(tpl, values):
    """{{key}} placeholders: a flat key from summary(), or a dotted spec path; unknown ones stay for the agent"""
    def one(m):
        k = m.group(1).strip(); v = values.get(k)
        if v is None and "." in k:
            v = values.get("_spec")
            for p in k.split("."): v = v.get(p) if isinstance(v, dict) else None
        return m.group(0) if v is None else (f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return re.sub(r"\{\{([^}]+)\}\}", one, tpl)


def handover(tpl):
    """what the script can't measure goes to the agent, keeping the template's hint: {{in/out}} -> [agent: in/out]"""
    return re.sub(r"\{\{(?!\.\.\.)([^}]+)\}\}", lambda m: f"[agent: {m.group(1).strip()}]", tpl)


def rows(tpl, marker, lines, drop=()):
    """the template's one example row (the line starting with marker) becomes one row per item; lines in drop go"""
    out = []
    for ln in tpl.split("\n"):
        if ln.startswith(marker): out += lines
        elif ln not in drop: out.append(ln)
    return "\n".join(out)


def cell(x, n=60): return str(x)[:n].replace("|", "/").replace("\n", " ")


def study_meta(video):
    """this reel's row in creator_study.py's study.json next to it (views, uploader), if there is one"""
    p = os.path.join(os.path.dirname(os.path.abspath(video)), "study.json"); vid = os.path.splitext(os.path.basename(video))[0]
    return next((r for r in (json.load(open(p)).get("reels", []) if os.path.exists(p) else []) if r.get("id") == vid), {})


def teardown(video, out, account=None):
    vid = os.path.splitext(os.path.basename(video))[0]; d = os.path.join(out, vid); os.makedirs(d, exist_ok=True)
    s = format_spec.measure(video, 2.0, os.path.join(d, "sheet.jpg")); meta = study_meta(video)
    s["study"] = {"views": meta.get("views"), "uploader": meta.get("uploader"), "url": meta.get("url")}
    json.dump(s, open(os.path.join(d, "spec.json"), "w"), ensure_ascii=False, indent=1)
    timeline(s, os.path.join(d, "timeline.png"))
    c, ev = s["cuts"], s["text"]["list"]; sm = summary(s)
    vals = {**sm, "_spec": s, "video": os.path.basename(video), "reel_id": vid, "w": s.get("w"), "h": s.get("h"),
            "account": account or meta.get("uploader") or "[agent: account]", "hook_end": f"{HOOK} (provisional)",
            "len(cuts.shot_cuts)": len(c.get("shot_cuts", [])), "len(cuts.insert_changes)": len(c.get("insert_changes", [])),
            'study.views or "not available"': meta.get("views") or "not available", "n_footage": "[agent: count]"}
    tpl = open(os.path.join(TPL, "report-template.md")).read()
    lab = sorted([(t, "shot") for t in c.get("shot_cuts", c["times"])] + [(t, "insert") for t in c.get("insert_changes", [])])
    tpl = rows(tpl, "| {{t}} | {{shot/insert}}", [f"| {round(t, 2)} | {k} | [agent] | [agent] | |" for t, k in lab] or ["| - | no cuts | | | |"])
    tpl = rows(tpl, "| {{t0}}–{{t1}} |", [f"| {e['t0']}–{e['t1']} | {cell(e['text'])} | [agent] | {e['y']} | {e['line_h']} | {e['rows']} | "
                                          f"{', '.join(e['plate']) or '-'} | {', '.join(e.get('letters', [])) or '-'} | measured |" for e in ev] or ["| - | no text | | | | | | | |"])
    starts = [0.0] + [round(t, 2) for t in c["times"]]
    sec = [f"| {i} | shot from {max(x for x in starts if x <= i)} s | | {cell(' / '.join(e['text'] for e in ev if e['t0'] <= i < e['t1']), 50) or '-'} | "
           f"{', '.join(str(round(t, 2)) for t in c['times'] if i <= t < i + 1) or '-'} | unknown (no transcript) |" for i in range(min(10, int(s['seconds']) + 1))]
    tpl = rows(tpl, "| 0 | {{frame_at_0}}", sec, drop=("| … | | | | | |",))
    open(os.path.join(d, "report.md"), "w").write(handover(fill(tpl, vals)))
    print(f"{vid}: {s['seconds']} s, speaker cuts {c.get('shot_cuts_per_min')}/min, {s['text']['events']} text events -> {d}")
    return s


def agg(xs, nd=1):
    """median (min-max) of the numbers in xs, '-' if none"""
    xs = [x for x in xs if isinstance(x, (int, float))]
    if not xs: return "-"
    r = lambda v: f"{round(v, nd):g}"
    return r(statistics.median(xs)) if min(xs) == max(xs) else f"{r(statistics.median(xs))} ({r(min(xs))}–{r(max(xs))})"


def competitors(accounts, out, owner="you"):
    specs = {n: [teardown(v, os.path.join(out, n), n) for src in srcs
                 for v in (sorted(glob.glob(os.path.join(src, "*.mp4"))) if os.path.isdir(src) else [src])] for n, srcs in accounts.items()}
    names = [n for n in specs if n != owner] + ([owner] if owner in specs else [])
    sums = {n: [summary(s) for s in specs[n]] for n in names}; views = {n: [s["study"]["views"] for s in specs[n] if s["study"]["views"]] for n in names}
    col = lambda f: " | ".join(f(n) for n in names)
    def accent(n):
        cs = [p for s in specs[n] for e in s["text"]["list"] for p in e["plate"]]
        return statistics.mode(cs) if cs else "none measured"
    table = [f"| field | {col(lambda n: f'{n} (n={len(sums[n])})')} | basis |", "|---|" + "---|" * (len(names) + 1)]
    for label, f, basis in [
            ("length (s)", lambda n: agg([x["seconds"] for x in sums[n]], 0), "measured"),
            ("hook end (s)", lambda n: "", "derived [agent]"), ("hook pattern", lambda n: "", "looked [agent]"),
            ("first own text (s)", lambda n: agg([x["first_text"] for x in sums[n]]), "measured (incl. footage text)"),
            ("body shot cuts / min", lambda n: agg([x["body_shot_per_min"] for x in sums[n]]), f"derived (after {HOOK} s, provisional)"),
            ("insert changes / min", lambda n: agg([x["insert_per_min"] for x in sums[n]]), "derived"),
            ("shot median / p90 (s)", lambda n: f"{agg([x['shot_median'] for x in sums[n]], 2)} / {agg([x['shot_p90'] for x in sums[n]], 2)}", "measured"),
            ("cuts land with clip changes", lambda n: "", "looked [agent]"),
            ("own text events / min", lambda n: agg([x["text_per_min"] for x in sums[n]]), "derived (incl. footage text)"),
            ("caption policy", lambda n: "", "looked [agent]"),
            ("accent colour", accent, "measured (most common plate) / looked"),
            ("face on screen", lambda n: agg([x["face_share"] for x in sums[n]], 2), "measured"),
            ("face height (shot scale)", lambda n: agg([x["face_height"] for x in sums[n]], 1), "measured"),
            ("layout mix", lambda n: "", "looked [agent]"),
            ("pauses / min · longest", lambda n: f"{agg([x['pauses_per_min'] for x in sums[n]])} · {agg([x['longest_pause'] for x in sums[n]])}", "measured"),
            ("CTA · end card · brand chrome", lambda n: f"fixed text in {sum(1 for x in sums[n] if x['chrome'])}/{len(sums[n])} reels" , "measured / looked"),
            ("views (median)", lambda n: agg(views[n], 0) if views[n] else "not available", "study")]:
        table.append(f"| {label} | {col(lambda n: cell(f(n), 40))} | {basis} |")
    tpl = open(os.path.join(os.path.dirname(TPL), "competitors", "report-template.md")).read()
    tpl = re.sub(r"\| field \| \{\{account A\}\}.*?\| views \(median\)[^\n]*", lambda m: "\n".join(table), tpl, flags=re.S)
    nv, nr = sum(map(len, views.values())), sum(map(len, sums.values()))
    tpl = re.sub(r"\{\{if 0:.*?\}\}", "" if nv else "No performance data; this comparison is descriptive.", tpl, flags=re.S)
    tpl = rows(tpl, "| {{account}} | {{n}}", [f"| {n} | {len(sums[n])} | [agent] | [agent] | [agent] | {len(views[n])} |" for n in names])
    a, b = tpl.index("### {{account}}"), tpl.index("## 3.")
    tpl = tpl[:a] + "".join(tpl[a:b].replace("{{account}}", n).replace("{{n}}", str(len(sums[n]))) for n in names) + tpl[b:]
    tpl = fill(tpl, {"owner": owner if owner in specs else "(no own reels given)", "accounts": ", ".join(n for n in names if n != owner),
                     "n_reels": nr, "n_reels_with_views": nv})
    json.dump({"accounts": sums, "views": views}, open(os.path.join(out, "compare.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(out, "compare.md"), "w").write(handover(tpl))
    print(f"compare: {', '.join(names)} -> {os.path.join(out, 'compare.md')}")


MARKERS = {"rea": ["| {{t}} | {{shot/insert}}", "| {{t0}}–{{t1}} |", "| 0 | {{frame_at_0}}"],
           "competitors": ["| field | {{account A}}", "| views (median)", "| {{account}} | {{n}}", "### {{account}}", "## 3.", "{{if 0:"]}


def check():
    """the templates still have the rows this script expands (they come from the method folder and can change), and the pure parts work"""
    for k, ms in MARKERS.items():
        t = open(os.path.join(os.path.dirname(TPL), k, "report-template.md")).read()
        assert all(m in t for m in ms), f"{k} template lost: {[m for m in ms if m not in t]}"
    s = {"seconds": 63.0, "cuts": {"times": [], "shot_cuts": [1.0, 4.0, 13.0, 33.0]}}
    assert body(s) == {"body_shot_n": 3, "body_shot_per_min": 3.0, "body_seconds": 60.0, "body_shot_median": 14.5}, body(s)
    assert rows("a\n| x |\nz", "| x", ["1", "2"]) == "a\n1\n2\nz"
    assert handover(fill("{{a}} {{b.c}} {{in/out}} {{...}}", {"a": 1.50, "_spec": {"b": {"c": 2}}})) == "1.5 2 [agent: in/out] {{...}}"
    assert agg([1, 3, 2]) == "2 (1–3)" and agg([4, 4]) == "4" and agg([None]) == "-"
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]: check(); sys.exit()
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["teardown", "competitors"]); ap.add_argument("items", nargs="+"); ap.add_argument("--out", required=True); ap.add_argument("--owner", default="you"); ap.add_argument("--account")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.mode == "teardown":
        for v in a.items: teardown(v, a.out, a.account)
    else:
        acc = {}
        for it in a.items:
            n, _, src = it.partition("="); acc.setdefault(n, []).append(src)
        competitors(acc, a.out, a.owner)
