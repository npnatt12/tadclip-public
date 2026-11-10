#!/usr/bin/env python3
"""Score format_spec.py's cuts against a reel TadClip built (its index.html says exactly when each take and each
full-frame insert starts): precision, recall, timing error. Ground truth from the build, not from anyone's opinion.
    cuts_truth.py <project dir with index.html> <spec.json> [--tol 0.2]"""
import json, re, sys
proj, spec = sys.argv[1], json.load(open(sys.argv[2])); tol = float(sys.argv[sys.argv.index("--tol") + 1]) if "--tol" in sys.argv else 0.2
h = open(f"{proj}/index.html").read()
takes = sorted(float(m) for m in re.findall(r'<video id="take-\d+"[^>]*data-start="([\d.]+)"', h))[1:]   # jump cuts: every take after the first
other = set()   # inserts and swipes: their starts and ends are cuts too, but which ones fill the frame isn't recorded here
for s0, d in re.findall(r'<video id="b\d+-v"[^>]*data-start="([\d.]+)"[^>]*data-duration="([\d.]+)"', h): other |= {float(s0), float(s0) + float(d)}
for s0 in re.findall(r'id="sw\d+" class="clip layer" data-start="([\d.]+)"', h): other.add(float(s0) + 0.3)
anyev = set(other) | set(takes)   # any scheduled visual change: an element appearing, a punch-in or push starting
anyev |= {float(m) for m in re.findall(r'id="[^"]+"[^>]*data-start="([\d.]+)"', h)}
anyev |= {float(m) for m in re.findall(r'tl\.(?:set|to|fromTo)\("#(?:push|punch)[^;]*?,\s*([\d.]+)\);', h)}
det = spec["cuts"]["times"]
near = lambda t, xs: min((abs(t - x) for x in xs), default=9) <= tol
found = [t for t in takes if near(t, det)]
explained = [t for t in det if near(t, takes) or near(t, other)]
err = [min(abs(t - x) for x in det) for t in found]
print(json.dumps({"takes": len(takes), "recall_takes": round(len(found) / max(1, len(takes)), 3), "detected": len(det),
                  "precision_vs_known_events": round(len(explained) / max(1, len(det)), 3),
                  "precision_vs_any_visual_change": round(sum(near(t, anyev) for t in det) / max(1, len(det)), 3),
                  "timing_err_median_s": round(sorted(err)[len(err) // 2], 3) if err else None,
                  "missed_takes": [round(t, 2) for t in takes if t not in found][:20],
                  "unexplained": [t for t in det if t not in explained][:20]}))
