"""Takes + Gemini-verified Thai text -> build/words.th.json (caption chunks spread over voiced time) + reel.json takes.
run from the project: "$(bash $S/scripts/lib/plat.sh thai)" -I build/cut.py (the Thai venv: mlxw on a Mac, fw on Windows)  (copy this file to $P/build/cut.py, replace TAKES)
One placeholder row shows the shape."""
import json, re, subprocess
from pythainlp.tokenize import word_tokenize

TAKES = [  # a, b (original s, on real pauses), verbatim text (Gemini 3 Flash, checked against whisper)
    (2.80, 7.70, "วางประโยคจากทรานสคริปต์ของคลิปนี้"),
]
if TAKES[0][:2] == (2.80, 7.70):  # choosing takes is the creative work: a copied list skips it silently
    raise SystemExit("TAKES is still the KG01 worked example: write this recording's takes from its transcript")
MAXC = 12  # ponytail: chars per caption chunk; tune if a line wraps
MARKS = re.compile(r"[ัิ-ฺ็-๎]")  # zero-width Thai vowel/tone marks: no spoken time

# micro-silences (same detector used to place the cuts)
log = subprocess.run(["ffmpeg", "-v", "info", "-i", "assets/talk.mp4", "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
sil = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", log)), map(float, re.findall(r"silence_end: ([\d.]+)", log))))


def voiced(a, b):
    """speech intervals inside [a, b]"""
    out, t = [], a
    for s, e in sil:
        if e <= t or s >= b: continue
        if s > t: out.append((t, s))
        t = max(t, e)
    if t < b: out.append((t, b))
    return out


def at(iv, frac):
    """time at fraction `frac` of the voiced duration"""
    tot = sum(e - s for s, e in iv); x = frac * tot
    for s, e in iv:
        if x <= e - s: return s + x
        x -= e - s
    return iv[-1][1]


segs = []
for a, b, text in TAKES:
    iv = voiced(a, b)
    toks = [t for t in word_tokenize(text, keep_whitespace=True)]
    weight = lambda s: len(MARKS.sub("", s.replace(" ", ""))) or 0
    total = sum(weight(t) for t in toks); acc = 0
    words = []
    for t in toks:
        w = weight(t)
        if t.strip(): words.append({"word": t.strip(), "start": at(iv, acc / total), "end": at(iv, (acc + w) / total), "sp": False})
        elif words: words[-1]["sp"] = True  # a space in the script = a phrase break
        acc += w
    chunks = []
    for w in words:
        c = chunks[-1] if chunks else None
        lat = w["word"].isascii()
        if c and w["word"] in "?!.,":
            c["word"] += w["word"]; c["sp"] = True; continue
        if c and not c["sp"] and not lat and not c["word"].isascii() and len(MARKS.sub("", c["word"] + w["word"])) <= MAXC:
            c["word"] += w["word"]; c["end"] = w["end"]; c["sp"] = w["sp"]
        else:
            chunks.append(dict(w))
    for c in chunks:
        c.pop("sp"); c["start"] = round(c["start"], 3); c["end"] = round(c["end"], 3)
    segs.append({"start": a, "end": b, "text": text, "words": chunks})

json.dump({"language": "th", "segments": segs}, open("build/words.th.json", "w"), ensure_ascii=False, indent=1)
json.dump([{"a": a, "b": b} for a, b, _ in TAKES], open("build/takes.json", "w"))
print(f"{len(TAKES)} takes, {sum(b - a for a, b, _ in TAKES):.2f} s of speech")
for s in segs: print(" | ".join(c["word"] for c in s["words"]))
