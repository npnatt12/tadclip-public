#!/usr/bin/env python3
"""Regression check for the 11-10 brand-intake test (docs/TEST-1110.md). Fails on the code before the fixes.
    python3 scripts/check_1110.py      (macOS: Vision, sips; ffmpeg, node 22, Pillow; ~20 s; writes only to a temp folder)
1. a brand sheet in the folder (an RGBA screenshot of hex codes on swatches) reaches the reel: every colour, the light main
   colour kept as the plate with the brand's own dark text, the style's transition in brand colours
2. a font file in the folder doesn't crash the loader (Pillow 12): the reel uses it
3. own.json edited by hand is re-made from the folder, with a build warning
4. a folder the loader can't read is a build warning, not a silent ClubGig"""
import json, os, re, shutil, subprocess, sys, tempfile
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(("ok  " if cond else "FAIL"), name, detail)
d = tempfile.mkdtemp(); P = os.path.join(d, "reel"); B = os.path.join(d, "TadClip", "brand")
os.makedirs(os.path.join(P, "assets")); os.makedirs(os.path.join(P, "build")); os.makedirs(B)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x445566:s=1080x1920:d=4:r=30", "-f", "lavfi", "-i", "sine=d=4",
                "-shortest", "-pix_fmt", "yuv420p", "-c:a", "aac", os.path.join(P, "assets", "talk.mp4")], check=True)
json.dump({"language": "th", "segments": [{"start": 0.2, "end": 3.5, "text": "สวัสดีครับ", "words": [{"word": "สวัสดีครับ", "start": 0.2, "end": 3.5}]}]},
          open(os.path.join(P, "build", "words.th.json"), "w"), ensure_ascii=False)
shutil.copy(os.path.join(S, "app", "test", "fixture", "brand-sheet.png"), os.path.join(B, "Screenshot 2569-11-10.png"))
shutil.copy(os.path.join(S, "app", "test", "fixture", "logo.png"), os.path.join(B, "logo.png"))
font = "/System/Library/Fonts/Supplemental/Ayuthaya.ttf"
if os.path.exists(font): shutil.copy(font, os.path.join(B, "Brand Font.ttf"))
spec = {"title": "check", "style": "clubgig", "source": "assets/talk.mp4", "words": "build/words.th.json", "takes": [{"a": 0, "b": 3.8}],
        "beats": [{"type": "impact", "at": 0.5, "to": 2.5, "text": "ข้อความ|{ของ}|{แบรนด์}"}, {"type": "broll", "at": 1.0, "to": 1.8, "src": "assets/talk.mp4", "swipe": True}]}
json.dump(spec, open(os.path.join(P, "reel.json"), "w"), ensure_ascii=False)
def build():
    r = subprocess.run(["node", os.path.join(S, "scripts", "build.mjs"), P], capture_output=True, text=True, env={**os.environ, "TADCLIP_DIR": os.path.join(d, "TadClip")})
    html = open(os.path.join(P, "index.html")).read() if os.path.exists(os.path.join(P, "index.html")) else ""
    return r.stdout + r.stderr, html
out, html = build()
k = json.load(open(os.path.join(P, "brand", "own.json"))) if os.path.exists(os.path.join(P, "brand", "own.json")) else {}
check("every colour on the sheet, in order", [c["hex"] for c in k.get("colors", {}).get("list", [])] == ["#00CCFF", "#A0ECFF", "#344054"], str(k.get("colors", {}).get("list")))
check("the light cyan stays the plate, with the brand's own dark text", 'background:#00CCFF"></i><b style="color:#344054' in html)
check("the stair's second plate is the light tint", 'background:#A0ECFF"></i><b style="color:#344054' in html)
check("the transition in brand colours, not ClubGig yellow", "#F2C230" not in html and "linear-gradient(180deg,#00CCFF" in html)
if os.path.exists(font): check("their font file is used (no Pillow crash)", k.get("font") == "Brandfont" and "brandfont-thai.ttf" in html, k.get("font_name", ""))
own = os.path.join(P, "brand", "own.json"); j = json.load(open(own)); j["impact"]["plate"] = "#123456"; json.dump(j, open(own, "w"))
out, html = build()
check("own.json edited by hand: re-made from the folder, and said", "changed by hand" in out and "#123456" not in open(own).read(), "")
os.makedirs(os.path.join(B, "brand.txt"))
out, html = build()
check("a folder the loader can't read: a build warning", "couldn't be read" in out, "")
shutil.rmtree(d); print("all ok" if ok else "FAILED"); sys.exit(0 if ok else 1)
