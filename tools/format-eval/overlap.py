#!/usr/bin/env python3
"""How much of a text reappears in a reference corpus: word n-gram containment and the longest shared run of words.
Used to show the clean-room method is not a copy or paraphrase-by-substitution of Hypit's guides (EVAL.md). The pass
line is fixed before the method is written: <= 1 % of the method's 8-word sequences found in the reference, and no
shared run of 15+ words.
    overlap.py <file or dir: the new text> <file or dir: the reference> [--n 8]"""
import os, re, sys
def words(p):
    fs = [p] if os.path.isfile(p) else [os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs if f.endswith((".md", ".json", ".yaml", ".svs", ".txt"))]
    out = {}
    for f in fs:
        t = open(f, errors="ignore").read().lower(); out[f] = re.findall(r"[a-z0-9฀-๿']+", t)
    return out
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 8
new, ref = words(sys.argv[1]), words(sys.argv[2])
refgrams = set(); refseq = []
for w in ref.values(): refgrams |= {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}; refseq.append(w)
tot = hit = 0; longest = (0, ""); shared = []
refjoined = [" " + " ".join(w) + " " for w in refseq]
for f, w in new.items():
    g = [tuple(w[i:i + n]) for i in range(len(w) - n + 1)]; h = [x in refgrams for x in g]
    tot += len(g); hit += sum(h)
    i = 0
    while i < len(h):   # grow each shared run to its full length
        if not h[i]: i += 1; continue
        j = i
        while j + 1 < len(h) and h[j + 1]: j += 1
        run = w[i:j + n]; s = " ".join(run)
        if any(" " + s + " " in r for r in refjoined): shared.append(s)
        if len(run) > longest[0]: longest = (len(run), s)
        i = j + 1
print(f"{n}-word sequences: {tot}, found in the reference: {hit} ({100 * hit / max(1, tot):.2f} %)")
print(f"longest shared run: {longest[0]} words" + (f": \"{longest[1][:160]}\"" if longest[0] else ""))
for s in sorted(set(shared), key=len, reverse=True)[:10]: print("  shared:", s[:140])
ok = hit / max(1, tot) <= 0.01 and longest[0] < 15
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
