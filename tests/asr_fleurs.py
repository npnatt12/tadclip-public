"""Real Thai speech, the same clips on every machine: Google FLEURS th_th dev (read speech by many speakers, CC-BY 4.0,
https://huggingface.co/datasets/google/fleurs), downloaded at test time (247 MB, cached), never redistributed. The first
N distinct sentences of dev.tsv go through TadClip's own transcribe.asr() (mlx_whisper on a Mac, faster-whisper on
Windows); CER against FLEURS' own transcript, spaces and punctuation ignored.
    python3 tests/asr_fleurs.py [--n 12] [--out result.json]        (FW_COMPUTE=int8|int8_float32|float32 on Windows)
One JSON line: engine, compute, CER, audio seconds, decode seconds, per-clip texts."""
import io, json, os, re, sys, tarfile, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts")); import transcribe   # noqa: E402
transcribe.ensure_mlx(__file__)
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 12
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "tadclip-fleurs-th"); os.makedirs(CACHE, exist_ok=True)
HF = "https://huggingface.co/datasets/google/fleurs/resolve/main/data/th_th/"


def get(name):
    p = os.path.join(CACHE, name.replace("/", "_"))
    if not os.path.exists(p):
        urllib.request.urlretrieve(HF + name, p + ".part"); os.replace(p + ".part", p)
    return p


rows, seen = [], set()
for ln in open(get("dev.tsv"), encoding="utf-8"):
    sid, wav, raw = ln.split("\t")[:3]
    if sid not in seen:
        seen.add(sid); rows.append((wav, raw))
    if len(rows) == N: break
want = {w for w, _ in rows}
if not all(os.path.exists(os.path.join(CACHE, w)) for w in want):
    with tarfile.open(get("audio/dev.tar.gz"), "r:gz") as t:
        for m in t:
            b = os.path.basename(m.name)
            if b in want: open(os.path.join(CACHE, b), "wb").write(t.extractfile(m).read())


def ed(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]


norm = lambda s: re.sub(r"[\s\.,!?\"'“”‘’()\-:;]", "", s).lower()
t = time.time(); engine, run = transcribe.asr("th"); load = time.time() - t
E = N_ = 0; audio = 0.0; texts = []; t = time.time()
for wav, ref in rows:
    x = transcribe.read16k(os.path.join(CACHE, wav)); audio += len(x) / 16000
    got = run(x, word_timestamps=True, condition_on_previous_text=False, temperature=(0.0, 0.2))["text"]
    E += ed(norm(got), norm(ref)); N_ += len(norm(ref)); texts.append(got.strip())
res = {"engine": engine, "compute": os.environ.get("FW_COMPUTE", "float32") if engine == "fw" else "-", "clips": len(rows), "cer": round(E / N_, 4),
       "audio_s": round(audio, 1), "load_s": round(load, 1), "decode_s": round(time.time() - t, 1), "texts": texts}
print(json.dumps(res, ensure_ascii=False))
if "--out" in sys.argv: json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
