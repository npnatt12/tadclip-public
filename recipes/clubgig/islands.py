#!/usr/bin/env python3
"""Speech islands from ffmpeg silencedetect (no venv needed) -> {"islands": [{a, b}]} for islands_tx.py --vad.
    islands.py assets/talk.mp4 build/vad.json [--db -35] [--min 0.35]
Without --db: -35 dB, and when that glues the talk into islands over 20 s (a noisy room: the 11-08 test clip gave one
290 s island), the gate moves up from the measured noise floor and it runs again.
ponytail: a dB gate; for very noisy rooms use vad_pauses.py (silero, the audio QA venv) instead."""
import array, json, math, re, subprocess, sys

src, out = sys.argv[1], sys.argv[2]
db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "-35"
mn = sys.argv[sys.argv.index("--min") + 1] if "--min" in sys.argv else "0.35"


def islands(db):
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
    return isl


def levels():
    """10th / 90th percentile loudness (dBFS) of 50 ms windows: the room's floor and the voice."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array.array("h"); a.frombytes(raw[: len(raw) // 2 * 2])
    lv = sorted(20 * math.log10(max(1.0, math.sqrt(sum(x * x for x in a[i:i + 400]) / 400)) / 32768) for i in range(0, len(a) - 400, 400))
    return lv[len(lv) // 10], lv[len(lv) * 9 // 10]


isl = islands(db)
if "--db" not in sys.argv and isl and max(i["b"] - i["a"] for i in isl) > 20:
    lo, hi = levels()
    long0 = max(i["b"] - i["a"] for i in isl)
    # the floor is RMS, silencedetect compares peaks (~10 dB higher): start 14 dB over it, step up, never past voice - 6
    for g in range(round(lo + 14), round(hi - 6) + 1, 3):
        db, isl = str(g), islands(str(g))
        if isl and max(i["b"] - i["a"] for i in isl) <= 20:
            break
    print(f"-35 dB kept a {long0:.0f} s island (noise floor {lo:.0f} dB, voice {hi:.0f} dB): gate at {db} dB")
json.dump({"islands": isl}, open(out, "w"))
print(f"{len(isl)} speech islands, {sum(i['b'] - i['a'] for i in isl):.1f} s of speech -> {out}")
