"""Every new style preset builds and renders (tests/style_examples.json: the beats each recipe's README shows).
A synthetic talk (test pattern + tone, like render_fixture.py) with generated stills: no one's footage.
    python3 tests/render_styles.py [--build-only] [--out DIR] [slug ...]
Prints one line per style; with --out, a still from the middle of its first beat (<slug>.png) and the mp4."""
import json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = json.load(open(os.path.join(ROOT, "tests", "style_examples.json"), encoding="utf-8"))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
build_only = "--build-only" in sys.argv
out_dir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
if out_dir:
    args = [a for a in args if a != out_dir]; os.makedirs(out_dir, exist_ok=True)
slugs = args or list(EX)
X264_THREADS = open(os.path.join(ROOT, "scripts", "X264_THREADS")).read().strip()
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
node = shutil.which("node"); bash = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH") or shutil.which("bash")


def shared(P):
    """the media every example uses, made once"""
    for d in ("assets/ins", "assets/broll", "build"): os.makedirs(os.path.join(P, d), exist_ok=True)
    ff("-f", "lavfi", "-i", "testsrc2=s=720x1280:r=30:d=12", "-f", "lavfi", "-i", "sine=f=220:d=12,volume='if(between(t,3.6,4.2),0,0.5)':eval=frame",
       "-c:v", "libx264", "-threads", X264_THREADS, "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", os.path.join(P, "assets", "talk.mp4"))
    ff("-f", "lavfi", "-i", "rgbtestsrc=s=1280x720:r=30:d=6", "-vf", "hue=H=2*PI*t/6", "-c:v", "libx264", "-threads", X264_THREADS, "-preset", "veryfast",
       "-pix_fmt", "yuv420p", os.path.join(P, "assets", "broll", "m1.mp4"))
    # a "whiteboard": white with a red underline drawing in
    ff("-f", "lavfi", "-i", "color=c=white:s=1280x720:r=30:d=6", "-vf", "drawbox=x=240:y=420:w='min(800,t*300)':h=10:color=red@1:t=fill",
       "-c:v", "libx264", "-threads", X264_THREADS, "-preset", "veryfast", "-pix_fmt", "yuv420p", os.path.join(P, "assets", "broll", "board.mp4"))
    for i, (a, b) in enumerate((("#E6B57A", "#6A2C3B"), ("#8FB0C8", "#2D3A4A")), 1):   # two "photos": a gradient with shapes
        ff("-f", "lavfi", "-i", f"gradients=s=1080x1350:c0={a}:c1={b}:d=1", "-vf", "drawbox=x=300:y=420:w=480:h=520:color=white@0.35:t=fill",
           "-frames:v", "1", os.path.join(P, "assets", "ins", f"photo{i}.jpg"))
    words = ["สวัสดี", "ครับ", "วันนี้", "จะ", "มา", "เล่า", "เรื่อง", "การ", "ตัด", "ต่อ", "คลิป", "ให้", "ง่าย", "ที่สุด"]
    W = [{"word": w, "start": round(0.6 + i * 0.48, 2), "end": round(0.6 + i * 0.48 + 0.4, 2), "probability": 0.95} for i, w in enumerate(words)]
    json.dump({"segments": [{"start": 0.6, "end": W[-1]["end"], "text": " ".join(words), "words": W}]},
              open(os.path.join(P, "build", "words.th.json"), "w", encoding="utf-8"), ensure_ascii=False)
    shutil.copy(os.path.join(ROOT, "app", "ui", "clubgig-wordmark-black.png"), os.path.join(P, "assets", "logo-black.png"))


base = tempfile.mkdtemp(prefix="tc-styles-"); shared(base)
bad = 0
for slug in slugs:
    ex = EX[slug]
    if ex.get("needs_matte") and not os.path.isdir(os.path.expanduser(os.environ.get("MATTE_VENV", "~/.venvs/tadclip-matte"))):
        print(f"skip {slug:<16} needs the person matte (bash scripts/setup_matte.sh)"); continue
    P = os.path.join(base, slug)
    shutil.copytree(base, P, ignore=lambda d, names: [n for n in names if n in EX])
    reel = {"title": f"style {slug}", "style": slug, "source": "assets/talk.mp4", "words": "build/words.th.json", "fps": 30, "outro": 1.0,
            "takes": [{"a": 0.4, "b": 11.6}],
            "beats": ex["beats"] + [{"type": "endcard", "at": "outro+0", "logo": "assets/logo-black.png", "bg": "#FFFFFF"}]}
    json.dump(reel, open(os.path.join(P, "reel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t0 = time.time()
    b = subprocess.run([node, os.path.join(ROOT, "scripts", "build.mjs"), P], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if b.returncode:
        bad += 1; print(f"FAIL {slug:<16} build: {(b.stderr or b.stdout).strip().splitlines()[-1][:200] if (b.stderr or b.stdout).strip() else b.returncode}"); continue
    if build_only:
        print(f"ok   {slug:<16} built in {time.time() - t0:.1f}s"); continue
    mp4 = os.path.join(out_dir or P, f"{slug}.mp4")
    r = subprocess.run([bash, os.path.join(ROOT, "scripts", "hf.sh"), "render", "-o", mp4], cwd=P, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode or not os.path.exists(mp4):
        bad += 1; print(f"FAIL {slug:<16} render: {(r.stderr or r.stdout)[-200:]}"); continue
    if out_dir:
        b0 = ex["beats"][0]; mid = (b0["at"] + b0["to"]) / 2 + 0.6
        ff("-ss", f"{mid:.2f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=360:-1", os.path.join(out_dir, f"{slug}.png"))
    print(f"ok   {slug:<16} built + rendered in {time.time() - t0:.1f}s")
sys.exit(1 if bad else 0)
