"""Mac vs Windows: is the Windows output the same reel? Limits fixed before the port (runs/2026-11-11-windows/PARITY.md).
    python3 tests/parity.py video  MAC.mp4 WIN.mp4              render: SSIM, cut points, loudness, duration
    python3 tests/parity.py words  MAC_islands.json WIN_islands.json [--ref ref-lines.json]
                                                                 Thai words: CER (vs a corrected reference), word timing
Prints one JSON line with "pass" and each number against its limit; exit 1 when a limit is missed."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIMITS = {"ssim_min": 0.95, "cut_ms": 100, "lufs": 1.0, "duration_s": 0.2, "cer_pt": 0.5, "word_ms": 100, "words_within": 0.95}


def lufs(p):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    return float(m[-1]) if m else None


def video(a, b):
    g = subprocess.run([sys.executable, os.path.join(HERE, "..", "scripts", "golden.py"), "video", a, b, "--min-ssim", str(LIMITS["ssim_min"])],
                       capture_output=True, text=True)
    j = json.loads(g.stdout.strip().splitlines()[-1])
    la, lb = lufs(a), lufs(b)
    moved = [m for m in j.get("cuts_moved", []) if not (isinstance(m[0], (int, float)) and abs(m[0] - m[1]) * 1000 <= LIMITS["cut_ms"])]
    r = {"ssim_min": j["ssim_min"], "ssim_mean": j["ssim_mean"], "frames": j["frames"], "cuts": j["cuts"], "cuts_moved": moved,
         "lufs": [la, lb], "duration": j["duration"]}
    r["pass"] = (j["ssim_min"] >= LIMITS["ssim_min"] and not moved and la is not None and lb is not None and abs(la - lb) <= LIMITS["lufs"]
                 and abs(j["duration"][0] - j["duration"][1]) <= LIMITS["duration_s"])
    return r


def ed(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]


def words(a, b, ref=None):
    import difflib
    L = lambda f: [w for i in json.load(open(f, encoding="utf-8")) for w in i["words"]]
    A, B = L(a), L(b)
    sm = difflib.SequenceMatcher(a=[w["w"] for w in A], b=[w["w"] for w in B], autojunk=False)
    d = sorted(abs(A[m.a + k]["a"] - B[m.b + k]["a"]) for m in sm.get_matching_blocks() for k in range(m.size))
    within = sum(x * 1000 <= LIMITS["word_ms"] for x in d) / max(len(d), 1)
    r = {"words": [len(A), len(B)], "matched": len(d), "start_within_100ms": round(within, 4)}
    if ref:   # [[a, b, "corrected line"], ...]: CER of each side (spaces ignored), cer.py's method
        R = json.load(open(ref, encoding="utf-8"))
        def cer(W):
            E = N = 0
            for x, y, t in R:
                h = "".join(w["w"] for w in W if x - 0.3 <= w["a"] <= y + 0.1).replace(" ", "").lower(); t = t.replace(" ", "").lower()
                E += ed(h, t); N += len(t)
            return E / N
        r["cer"] = [round(cer(A), 4), round(cer(B), 4)]
    r["pass"] = within >= LIMITS["words_within"] and (not ref or r["cer"][1] - r["cer"][0] <= LIMITS["cer_pt"] / 100)
    return r


if __name__ == "__main__":
    kind, a, b = sys.argv[1:4]
    ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
    r = video(a, b) if kind == "video" else words(a, b, ref)
    print(json.dumps({"kind": kind, "limits": LIMITS, **r}, ensure_ascii=False))
    sys.exit(0 if r["pass"] else 1)
