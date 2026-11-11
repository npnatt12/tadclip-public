"""A small synthetic ClubGig reel built and rendered end to end (build.mjs -> HyperFrames -> mp4), for comparing a render
across machines (Mac vs Windows): Thai text through Chrome's fonts, captions, an impact card, the logo, the voice mix.
No one's footage: the 'talk' clip is a test pattern with a tone.
    python3 tests/render_fixture.py <out.mp4> [--keep DIR]
Prints one JSON line: seconds to build and to render, the output's duration/size/loudness."""
import json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1]); keep = sys.argv[sys.argv.index("--keep") + 1] if "--keep" in sys.argv else None
P = keep or tempfile.mkdtemp(prefix="tc-render-")
for d in ("assets/ins", "assets/broll", "build"): os.makedirs(os.path.join(P, d), exist_ok=True)
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
X264_THREADS = open(os.path.join(ROOT, "scripts", "X264_THREADS")).read().strip()   # pinned like every encode (doctor.sh checks)
# 12 s 'talk': moving test pattern + a voice-band tone that pauses (so the mix and loudness have something to measure);
# two stock stand-ins for the hook split and the swiped B-roll (ClubGig's gate wants both)
ff("-f", "lavfi", "-i", "testsrc2=s=720x1280:r=30:d=12", "-f", "lavfi", "-i", "sine=f=220:d=12,volume='if(between(t,3.6,4.2),0,0.5)':eval=frame",
   "-c:v", "libx264", "-threads", X264_THREADS, "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", os.path.join(P, "assets", "talk.mp4"))
for name, src in (("ins/hook.mp4", "smptehdbars=s=1280x720:r=30:d=4"), ("broll/m1.mp4", "rgbtestsrc=s=1280x720:r=30:d=4")):
    ff("-f", "lavfi", "-i", src, "-vf", "hue=H=2*PI*t/4", "-c:v", "libx264", "-threads", X264_THREADS, "-preset", "veryfast", "-pix_fmt", "yuv420p", os.path.join(P, "assets", name))
words = ["สวัสดี", "ครับ", "วันนี้", "จะ", "มา", "เล่า", "เรื่อง", "การ", "ตัด", "ต่อ", "คลิป", "ให้", "ง่าย", "ที่สุด"]
W = [{"w": w, "a": round(0.6 + i * 0.48, 2), "b": round(0.6 + i * 0.48 + 0.4, 2), "p": 0.95} for i, w in enumerate(words)]
json.dump({"segments": [{"start": 0.6, "end": W[-1]["b"], "text": " ".join(words), "words": [{"word": w["w"], "start": w["a"], "end": w["b"], "probability": w["p"]} for w in W]}]},
          open(os.path.join(P, "build", "words.th.json"), "w", encoding="utf-8"), ensure_ascii=False)   # whisper json, as build.mjs reads it
shutil.copy(os.path.join(ROOT, "app", "ui", "clubgig-wordmark-white.png"), os.path.join(P, "assets", "logo.png"))
shutil.copy(os.path.join(ROOT, "app", "ui", "clubgig-wordmark-black.png"), os.path.join(P, "assets", "logo-black.png"))
reel = {"title": "render fixture", "style": "clubgig", "source": "assets/talk.mp4", "words": "build/words.th.json", "fps": 30, "outro": 1.2,
        "takes": [{"a": 0.4, "b": 11.6}],
        "beats": [{"type": "broll", "src": "assets/ins/hook.mp4", "at": 0.5, "to": 2.6, "mode": "split", "h": 900, "shift": 380, "zoom": [1.0, 1.06]},
                  {"type": "impact", "look": "qcard", "role": "question", "at": 0.5, "to": 2.8, "text": "ตัดต่อคลิป|{ยากไหม?}"},
                  {"type": "impact", "at": 3.4, "to": 5.4, "text": "TadClip|ทำให้เอง", "role": "topic", "push": True},
                  {"type": "broll", "src": "assets/broll/m1.mp4", "at": 5.8, "to": 8.2, "swipe": True, "label": ["TadClip", "ตัดต่อให้เอง"]},
                  {"type": "linecta", "at": 9.0, "lines": ["ทักไลน์", "รับคู่มือฟรี"], "handle": "@TADCLIP"},
                  {"type": "endcard", "at": "outro+0", "logo": "assets/logo-black.png", "bg": "#FFFFFF"}],
        "chrome": {"left": "GROWTH\nINSPIRATION\nGRACE", "logo": "assets/logo.png", "logoW": 210}}
json.dump(reel, open(os.path.join(P, "reel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
node = shutil.which("node"); t0 = time.time()
b = subprocess.run([node, os.path.join(ROOT, "scripts", "build.mjs"), P], capture_output=True, text=True, encoding="utf-8")
if b.returncode: sys.exit("build failed:\n" + b.stderr[-2000:] + b.stdout[-1000:])
t1 = time.time()
bash = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH") or shutil.which("bash") or sys.exit("no bash (Git Bash on Windows)")
r = subprocess.run([bash, os.path.join(ROOT, "scripts", "hf.sh"), "render", "-o", out], cwd=P, capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode or not os.path.exists(out): sys.exit("render failed:\n" + (r.stderr or "")[-3000:] + (r.stdout or "")[-2000:])
t2 = time.time()
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", out], capture_output=True, text=True).stdout)["format"]
lu = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = next((l.split("I:")[1].split("LUFS")[0].strip() for l in reversed(lu.splitlines()) if l.strip().startswith("I:")), None)
print(json.dumps({"build_s": round(t1 - t0, 1), "render_s": round(t2 - t1, 1), "duration": float(pr["duration"]), "bytes": int(pr["size"]), "lufs": float(I) if I else None}))
if not keep: shutil.rmtree(P, ignore_errors=True)
