"""golden.py: video catches changed frames, a short video track and a wrong fps; check never writes the project. Synthetic."""
import subprocess, sys, tempfile
from pathlib import Path

G = Path(__file__).resolve().parent.parent / "scripts/golden.py"


def clip(path, cut_at):
    # two colour shots joined at cut_at seconds, 2 s total, 30 fps
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=180x320:r=30:d=2",
                    "-vf", f"drawbox=c=red:t=fill:enable='gte(t,{cut_at})'", "-pix_fmt", "yuv420p", str(path)], check=True)


def run(a, b):
    return subprocess.run([sys.executable, str(G), "video", str(a), str(b)], capture_output=True, text=True).returncode


def test_video():
    with tempfile.TemporaryDirectory() as d:
        a, b, c = (Path(d) / f"{n}.mp4" for n in "abc")
        clip(a, 1.0); clip(b, 1.0); clip(c, 1.3)
        assert run(a, b) == 0, "identical renders must pass"
        assert run(a, c) == 1, "a moved cut / changed frames must fail"


def test_video_track():
    with tempfile.TemporaryDirectory() as d:
        a, short, fast = (Path(d) / f"{n}.mp4" for n in ("a", "short", "fast"))
        mk = lambda p, dur, r: subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s=180x320:r={r}:d={dur}", "-f", "lavfi", "-i", "sine=d=3",
                                               "-pix_fmt", "yuv420p", "-c:a", "aac", str(p)], check=True)
        mk(a, 3, 30); mk(short, 2.5, 30); mk(fast, 3, 60)
        assert run(a, short) == 1, "a video track that stops early must fail, whatever the container says"
        assert run(a, fast) == 1, "a different frame rate must fail"


def test_check_never_writes_the_project():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        skill, real, gold = d / "skill", d / "real", d / "gold"
        (skill / "scripts").mkdir(parents=True); real.mkdir(); gold.mkdir()
        (skill / "scripts/build.mjs").write_text('import fs from "node:fs"; const p = process.argv[2];'
                                                 'fs.writeFileSync(p + "/index.html", fs.readFileSync(p + "/reel.json"));')
        (real / "reel.json").write_text("orig"); (gold / "reel.json").write_text("frozen"); (gold / "index.html").write_text("frozen")
        link = d / "link"; link.symlink_to(real)
        r = subprocess.run([sys.executable, str(G), "check", str(link), str(gold), "--skill", str(skill)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert (real / "reel.json").read_text() == "orig" and not (real / "index.html").exists(), "check wrote through the symlink"
        (gold / "index.html").write_text("other")
        r = subprocess.run([sys.executable, str(G), "check", str(real), str(gold), "--skill", str(skill)], capture_output=True, text=True)
        assert r.returncode == 1 and "frozen" in r.stdout, "a failure must show the change: " + r.stdout
        assert not list(gold.glob("golden-*")), "temp folder left behind"


if __name__ == "__main__":
    test_video(); test_video_track(); test_check_never_writes_the_project(); print("ok")
