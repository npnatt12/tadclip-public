"""Thai speech-to-text on a machine without mlx (the Windows question): faster-whisper large-v3-turbo, CPU, on 8 synthetic
Thai sentences (macOS voice Kanya, fixture/). Character error rate vs the typed text, and wall time.
   python tools/winprobe/asr_probe.py [model] [compute]
Synthetic speech is clean and easier than a phone recording: this measures speed and that the stack runs, not real accuracy
(that's IMG_2260 on the Mac, runs/2026-11-12-release/windows)."""
import json, os, platform, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, "fixture")
model = sys.argv[1] if len(sys.argv) > 1 else "large-v3-turbo"; compute = sys.argv[2] if len(sys.argv) > 2 else "int8"
def ed(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]
t = time.time(); m = WhisperModel(model, device="cpu", compute_type=compute); load = time.time() - t
E = N = 0; t = time.time(); audio = 0.0
for r in json.load(open(os.path.join(F, "ref.json"), encoding="utf8")):
    # decoded by ffmpeg, not faster-whisper's PyAV: av 16 dropped the metadata_errors argument it passes (11-12)
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(F, r["wav"]), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                     capture_output=True, check=True).stdout, np.float32)
    segs, info = m.transcribe(x, language="th", word_timestamps=True, condition_on_previous_text=False, temperature=[0.0, 0.2], beam_size=5)
    h = "".join(s.text for s in segs).replace(" ", ""); ref = r["text"].replace(" ", "")
    E += ed(h, ref); N += len(ref); audio += info.duration
    print(f"  {ed(h, ref):3d}/{len(ref):3d}  {h}")
dec = time.time() - t
print(f"RESULT {platform.system()} {platform.machine()} cpus={os.cpu_count()} {model} {compute}: CER {E / N:.1%} over {N} chars; "
      f"load {load:.0f} s, decode {dec:.0f} s for {audio:.0f} s of audio ({dec / audio:.2f}x real time)")
