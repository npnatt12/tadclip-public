#!/usr/bin/env python3
"""Agreement between editors (the ceiling) and between the engine and the editors, field by field.
    agree.py annotations.csv <specs dir>     (specs: format_spec.py JSON named <reel without extension>.json)
Counts agree when within 20 % (or 1); categories when equal. The engine's answers come from the measurements:
speaker_cuts = cuts.shot_cuts, inserts = cuts.insert_changes, text_where = the zone with most text time,
text_plate = most text time on a plate, captions_word_by_word = text events shorter than 1.2 s on median,
first_text_s = text.first_seen. music isn't measured yet."""
import csv, itertools, json, os, sys, collections
rows = list(csv.DictReader(open(sys.argv[1]))); specs = sys.argv[2]
def engine(reel):
    s = json.load(open(os.path.join(specs, os.path.splitext(reel)[0] + ".json"))); t = s["text"]; ev = t["list"]
    plated = sum(e["t1"] - e["t0"] for e in ev if e.get("plate")); total = sum(e["t1"] - e["t0"] for e in ev) or 1
    z = max(t["zones"], key=t["zones"].get) if t["zones"] else "none"
    return {"speaker_cuts": len(s["cuts"].get("shot_cuts", s["cuts"]["times"])), "inserts": len(s["cuts"].get("insert_changes", [])),
            "text_where": {"no-face": "lower"}.get(z, z), "text_plate": "yes" if plated / total > 0.5 else "no",
            "captions_word_by_word": "yes" if (t.get("seconds_median") or 9) < 1.2 else "no", "first_text_s": t.get("first_seen")}
def same(f, a, b):
    if a in (None, "") or b in (None, ""): return None
    if f in ("speaker_cuts", "inserts", "first_text_s"):
        a, b = float(a), float(b); return abs(a - b) <= max(1, 0.2 * max(a, b))
    return str(a).strip().lower() == str(b).strip().lower()
F = ["speaker_cuts", "inserts", "text_where", "text_plate", "captions_word_by_word", "first_text_s"]
by = collections.defaultdict(list)
for r in rows: by[r["reel"]].append(r)
human, mach = collections.defaultdict(list), collections.defaultdict(list)
for reel, rs in by.items():
    e = engine(reel)
    for f in F:
        for a, b in itertools.combinations(rs, 2):
            x = same(f, a[f], b[f]); x is not None and human[f].append(x)
        for a in rs:
            x = same(f, a[f], e[f]); x is not None and mach[f].append(x)
print(f"{'field':24} editors vs editors   engine vs editors")
for f in F:
    h, m = human[f], mach[f]
    print(f"{f:24} {(f'{100 * sum(h) / len(h):.0f} % of {len(h)}') if h else '-':20} {(f'{100 * sum(m) / len(m):.0f} % of {len(m)}') if m else '-'}")
