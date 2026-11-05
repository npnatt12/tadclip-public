#!/usr/bin/env python3
"""Speech islands from ffmpeg silencedetect (no venv needed) -> {"islands": [{a, b}]} for islands_tx.py --vad.
    islands.py assets/talk.mp4 build/vad.json [--db -35] [--min 0.35]
ponytail: a dB gate; for noisy rooms use vad_pauses.py (silero, the audio QA venv) instead."""
import json, re, subprocess, sys

src, out = sys.argv[1], sys.argv[2]
db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "-35"
mn = sys.argv[sys.argv.index("--min") + 1] if "--min" in sys.argv else "0.35"
log = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-af", f"silencedetect=noise={db}dB:d={mn}", "-f", "null", "-"], capture_output=True, text=True).stderr
dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", log).groups()[2]) + 60 * int(re.search(r"Duration: (\d+):(\d+)", log).group(2)) + 3600 * int(re.search(r"Duration: (\d+)", log).group(1))
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
isl, t = [], 0.0
for s, e in zip(starts, ends + [dur]):
    if s - t > 0.25:
        isl.append({"a": round(t, 3), "b": round(s, 3)})
    t = e
if dur - t > 0.25:
    isl.append({"a": round(t, 3), "b": round(dur, 3)})
json.dump({"islands": isl}, open(out, "w"))
print(f"{len(isl)} speech islands, {sum(i['b'] - i['a'] for i in isl):.1f} s of speech -> {out}")
