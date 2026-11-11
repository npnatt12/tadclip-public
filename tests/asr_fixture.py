"""Thai speech-to-text through TadClip's own code path (transcribe.asr: mlx_whisper on a Mac, faster-whisper on Windows) on
the 8 synthetic Thai sentences in tools/winprobe/fixture. Prints one JSON line: engine, CER vs the typed text, seconds,
and the texts (to compare machines).   python3 tests/asr_fixture.py [--out result.json]
Synthetic speech is clean: this checks the engine runs and agrees across machines, not real accuracy (IMG_2260 does that)."""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts")); import transcribe   # noqa: E402
transcribe.ensure_mlx(__file__)
F = os.path.join(ROOT, "tools", "winprobe", "fixture")


def ed(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]


t = time.time(); engine, run = transcribe.asr("th"); load = time.time() - t
E = N = 0; texts = []; t = time.time()
for r in json.load(open(os.path.join(F, "ref.json"), encoding="utf-8")):
    x = transcribe.read16k(os.path.join(F, r["wav"]))
    got = run(x, word_timestamps=True, condition_on_previous_text=False, temperature=(0.0, 0.2))["text"].replace(" ", "")
    ref = r["text"].replace(" ", ""); E += ed(got, ref); N += len(ref); texts.append(got)
res = {"engine": engine, "cer": round(E / N, 4), "load_s": round(load, 1), "decode_s": round(time.time() - t, 1), "texts": texts}
print(json.dumps(res, ensure_ascii=False))
if "--out" in sys.argv: json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
