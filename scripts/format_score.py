#!/usr/bin/env python3
"""Score a reel's measurements against a saved creator format (docs/format-engine/method/METHOD.md, part 4): every
format field whose source is a plain spec path (cuts.per_min, face.top, ...) is checked against its accept band:
inside = 1, outside = max(0, 1 - distance / band width). Fields read off the contact sheet or derived by an agent
are listed for the critic agent, not scored here.
    format_score.py <format.json> <spec.json>      (spec: format_spec.py on the finished reel)"""
import json, re, sys
fmt, spec = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
def get(path):
    x = spec
    for k in path.split("."): x = x.get(k) if isinstance(x, dict) else None
    return x
rows, skipped = [], []
def walk(x, p):
    if isinstance(x, dict):
        if isinstance(x.get("accept"), list) and len(x["accept"]) == 2 and x.get("basis") == "measured":
            src = str(x.get("source", ""))
            if re.fullmatch(r"[a-z_]+(\.[a-z_]+)*", src) and isinstance(get(src), (int, float)):
                lo, hi = x["accept"]; v = float(get(src)); w = max(hi - lo, 1e-6)
                s = 1.0 if lo <= v <= hi else max(0.0, 1 - min(abs(v - lo), abs(v - hi)) / w)
                rows.append((p.strip("."), src, v, lo, hi, round(s, 2)))
            else: skipped.append(p.strip("."))
        for k, v in x.items(): walk(v, f"{p}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x): walk(v, f"{p}[{i}]")
walk(fmt, "")
for r in rows: print(f"{'ok ' if r[5] == 1 else 'OUT'} {r[0]:28} {r[1]:22} {r[2]:>8} in [{r[3]}, {r[4]}]  score {r[5]}")
m = sum(r[5] for r in rows) / max(1, len(rows))
print(f"\nmeasured fields in range: {sum(r[5] == 1 for r in rows)} / {len(rows)}, mean score {m:.2f}; "
      f"{len(skipped)} fields left to the critic (contact sheet, roles, devices)")
