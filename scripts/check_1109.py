#!/usr/bin/env python3
"""Regression check for the 11-09 evening new-user test (docs/TEST-1109.md). Fails on the code before the fixes.
    python3 scripts/check_1109.py          (needs ffmpeg, node 22, Pillow; ~20 s; writes only to a temp folder)
1. the Whisper model default resolves on a fresh install (it named a folder no install has); looping text is dropped
2. a Thai reel in the plain/clean style: captions ~2x (128 px), one phrase per screen, a Thai font (Kanit)
3. the user's brand folder reaches a non-ClubGig style through build.mjs alone: own.json made, their logo on an end card
4. a captions.size under 100 px for Thai without captions.asked is a build warning"""
import json, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(S, "scripts"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(("ok  " if cond else "FAIL"), name, detail)

import transcribe, islands_tx
m = transcribe.MLX_MODEL
check("a looping transcript (a breath read as 'ที่สุด' x50) is dropped", islands_tx.looping("ท ี่ ส ุ ด " * 8) and not islands_tx.looping("ประทับใจในการทำงานกับบูตะมากครับ"))
check("whisper model default resolves", os.path.isdir(os.path.expanduser(m)) or (m.count("/") == 1 and not m.startswith(("~", "/"))), m)

d = tempfile.mkdtemp(); P = os.path.join(d, "reel"); B = os.path.join(d, "TadClip", "brand")
os.makedirs(os.path.join(P, "assets")); os.makedirs(os.path.join(P, "build")); os.makedirs(B)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x445566:s=1080x1920:d=4:r=30", "-f", "lavfi", "-i", "sine=d=4",
                "-shortest", "-pix_fmt", "yuv420p", "-c:a", "aac", os.path.join(P, "assets", "talk.mp4")], check=True)
chunks = [("สวัสดีครับวันนี้", 0.2, 1.4), ("จะมาเล่าเรื่อง", 1.5, 2.6), ("การทำคลิป", 2.7, 3.7)]
json.dump({"language": "th", "segments": [{"start": a, "end": b, "text": t, "words": [{"word": t, "start": a, "end": b}]} for t, a, b in chunks]},
          open(os.path.join(P, "build", "words.th.json"), "w"), ensure_ascii=False)
logo = Image.new("RGBA", (600, 300)); ImageDraw.Draw(logo).ellipse([150, 50, 450, 250], fill=(20, 110, 200, 255)); logo.save(os.path.join(B, "logo.png"))
spec = {"title": "check", "style": "clean", "source": "assets/talk.mp4", "words": "build/words.th.json", "takes": [{"a": 0, "b": 3.8}],
        "captions": {"style": "clean"}, "beats": []}
def build(sp):
    json.dump(sp, open(os.path.join(P, "reel.json"), "w"), ensure_ascii=False)
    r = subprocess.run(["node", os.path.join(S, "scripts", "build.mjs"), P], capture_output=True, text=True, env={**os.environ, "TADCLIP_DIR": os.path.join(d, "TadClip")})
    return r.stdout + r.stderr, open(os.path.join(P, "index.html")).read() if os.path.exists(os.path.join(P, "index.html")) else ""
out, html = build(spec)
css = re.search(r"\.cap-group \{ font-family: ([^;]+); font-size: (\d+)px", html)
check("Thai captions 2x by default", css and int(css[2]) >= 110, css and css[2] + " px")
check("Thai captions in a Thai font", css and css[1].startswith("Kanit"), css and css[1])
groups = len(re.findall(r'id="cg\d+"', html))
check("one phrase per caption", groups == len(chunks), f"{groups} groups for {len(chunks)} phrases")
check("their brand applied by build.mjs (own.json made)", os.path.exists(os.path.join(P, "brand", "own.json")), "")
check("their logo on an end card in a style that has none", "own-logo-card.png" in html, "")
out2, _ = build({**spec, "captions": {"style": "clean", "size": 62}})
check("a small Thai caption size is a warning", "hard to read on a phone" in out2, "")
print("all ok" if ok else "FAILED"); sys.exit(0 if ok else 1)
