#!/usr/bin/env python3
"""Golden regression for reel builds: a skill change must not move an approved reel.

  golden.py freeze PROJECT DIR [--preview FILE]   frozen reel.json + index.html (+ preview) + manifest.json
  golden.py check  PROJECT DIR [--skill S]        rebuild the frozen reel.json with S's build.mjs on an APFS clone
                                                  of PROJECT; PASS = index.html byte-identical to the frozen one
  golden.py video  A.mp4 B.mp4 [--min-ssim 0.94]  per-frame SSIM + scene-cut times; PASS = same length, every frame
                                                  >= min SSIM, cuts within one frame; frames under 0.98 are listed
                                                  as noise (renderer jitter where a stock clip starts or a swipe
                                                  blurs the plate measured 0.948-0.98 on an unchanged composition)

Exit 0 = PASS, 1 = FAIL. The project is never written: check works on a copy-on-write clone it deletes after.

What this does NOT catch (independent review, 2026-11-05):
  check   compares index.html only. A skill change to a font or SFX file's contents, or to build/*.json, still passes,
          and the clone keeps the project's old assets/. Only reel.json is frozen, so a changed words file shows up as a
          skill regression. Hashes in manifest.json are a record, not checked again.
  video   is a coarse sanity check on masters, not a pass/fail bar for a reel. Whole-frame SSIM can't see a small overlay
          change (a 500x120 box scored 0.985) and audio is not compared at all. scdet finds hard cuts, not same-framing
          jump cuts: compare build_report.json takes for those. A human still watches the render.
"""
import argparse, difflib, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def freeze(a):
    d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
    files = {n: Path(a.project, n) for n in ("reel.json", "index.html")}
    if a.preview: files["preview.mp4"] = Path(a.preview)
    for n, p in files.items(): shutil.copy2(p, d / n)
    commit = subprocess.run(["git", "-C", str(SKILL), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    (d / "manifest.json").write_text(json.dumps(
        {"project": str(Path(a.project).resolve()), "skill_commit": commit, "sha256": {n: sha(d / n) for n in files}}, indent=1))
    print(f"frozen {len(files)} files at skill {commit[:7]} -> {d}")
    return 0


def check(a):
    d, skill = Path(a.dir), Path(a.skill or SKILL)
    tmp = Path(tempfile.mkdtemp(prefix="golden-", dir=d))
    work = tmp / "p"
    try:
        # ponytail: APFS clone (cp -c) so an 800 MB project costs no disk; macOS only, plain copy elsewhere.
        # resolve(): cp -R keeps a symlink as a link, and the build would then write through it into the real project
        if sys.platform == "darwin":
            subprocess.run(["cp", "-c", "-R", str(Path(a.project).resolve()), str(work)], check=True)
        else:
            shutil.copytree(Path(a.project).resolve(), work)
        shutil.copy2(d / "reel.json", work / "reel.json")
        b = subprocess.run(["node", str(skill / "scripts/build.mjs"), str(work)], capture_output=True, text=True)
        if b.returncode:
            print("FAIL build:", b.stderr.strip()[-800:]); return 1
        rep = work / "build/build_report.json"
        warns = json.loads(rep.read_text()).get("warnings", []) if rep.exists() else []
        old, new = (d / "index.html").read_bytes(), (work / "index.html").read_bytes()
        if old == new:
            print(f"PASS index.html identical ({len(new)} bytes), {len(warns)} build warnings"); return 0
        tags = lambda x: x.decode("utf-8", "replace").replace(">", ">\n").splitlines()
        diff = [l for l in difflib.unified_diff(tags(old), tags(new), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))][:12]
        print(f"FAIL index.html differs ({len(old)} vs {len(new)} bytes); first changes:\n" + "\n".join(diff)); return 1
    finally:
        shutil.rmtree(tmp)


def ff(args, cwd=None):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True, cwd=cwd)
    if r.returncode:  # a failed analysis must not read as a clean one
        sys.exit("ffmpeg failed: " + r.stderr.strip()[-400:])
    return r.stderr


def stream(p):
    """(seconds, fps) of the video track: the container length hides a video that stops early."""
    fr, sec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,duration", "-of", "csv=p=0:nk=1", p],
                             capture_output=True, text=True).stdout.strip().split(",")[:2]
    n, m = fr.split("/")
    return float(sec), float(n) / float(m)


def cuts(p, thr=10):
    return [float(t) for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", ff(["-i", p, "-vf", f"scdet=threshold={thr}", "-an", "-f", "null", "-"]))]


def video(a):
    # the stats file by a bare name in a temp folder: a Windows path's "C:" ends an ffmpeg filter option, and an open
    # NamedTemporaryFile can't be written by another process on Windows
    with tempfile.TemporaryDirectory() as td:
        ff(["-i", os.path.abspath(a.a), "-i", os.path.abspath(a.b), "-lavfi", "[0:v][1:v]ssim=stats_file=ssim.log", "-f", "null", "-"], cwd=td)
        s = [float(m) for m in re.findall(r"All:([\d.]+)", Path(td, "ssim.log").read_text())]
    (da, fa), (db, fb) = stream(a.a), stream(a.b)
    ca, cb = cuts(a.a), cuts(a.b)
    fps_tol = 1 / fa + 1e-3
    moved = [(x, y) for x, y in zip(ca, cb) if abs(x - y) > fps_tol] + ([("count", f"{len(ca)} vs {len(cb)}")] if len(ca) != len(cb) else [])
    bad = [(i, v) for i, v in enumerate(s) if v < a.min_ssim]
    noise = [round(i / fa, 2) for i, v in enumerate(s) if a.min_ssim <= v < 0.98]
    ok = abs(da - db) <= fps_tol and abs(fa - fb) < 0.01 and not bad and not moved and len(s) >= round(min(da, db) * fa) - 1
    print(json.dumps({"pass": bool(ok), "duration": [da, db], "fps": [fa, fb], "frames": len(s), "ssim_mean": round(sum(s) / max(len(s), 1), 5),
                      "ssim_min": round(min(s, default=0), 5), "frames_below": len(bad), "first_below_s": [round(i / fa, 2) for i, _ in bad[:8]],
                      "noise_frames": len(noise), "noise_first_s": noise[:8], "cuts": [len(ca), len(cb)], "cuts_moved": moved[:8]}))
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    f = sp.add_parser("freeze"); f.add_argument("project"); f.add_argument("dir"); f.add_argument("--preview")
    c = sp.add_parser("check"); c.add_argument("project"); c.add_argument("dir"); c.add_argument("--skill")
    v = sp.add_parser("video"); v.add_argument("a"); v.add_argument("b"); v.add_argument("--min-ssim", type=float, default=0.94)  # ponytail: one global floor; per-window masks if noise grows
    a = p.parse_args()
    sys.exit({"freeze": freeze, "check": check, "video": video}[a.cmd](a))


if __name__ == "__main__":
    main()
