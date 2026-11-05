#!/usr/bin/env python3
"""Fetch a creator's reels (or one viral video) and study how they are edited.

    creator_study.py <video url> [<video url> ...] --out DIR
    creator_study.py @handle --youtube --out DIR [--n 3]

Writes into DIR, per video: <id>.mp4 and <id>/ (reference_study.py: sheet.jpg, frames/, edit-log.txt when Gemini
answers), and study.json: where each came from, its length and cuts per minute (measured here, not by a model).

A bare handle means Instagram, and Instagram and TikTok refuse logged-out profile listing, so give video links: the Chrome
tools read them off the profile page, or the user pastes them. Single reels download logged out. --youtube lists a
channel's most-viewed recent Shorts, only when the user says the creator is on YouTube: the same handle there can be
someone else entirely (measured 2026-11-05: @itstundeanthony on YouTube was not the Instagram creator).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = 15  # recent Shorts to rank by views
# YouTube answers 403 to a yt-dlp a few months old (measured 2026-11-05: 2026.07.04 fails, 2026.10.26 + node works), so always run the latest
YT = ["uvx", "--from", "yt-dlp[default]@latest", "yt-dlp", "--js-runtimes", "node"] if shutil.which("uvx") else ["yt-dlp"]


def shorts_url(arg):
    """@handle -> its Shorts tab; None for anything that is not a handle."""
    return f"https://www.youtube.com/@{arg[1:]}/shorts" if re.fullmatch(r"@[\w.-]+", arg) else None


def top_by_views(entries, n):
    return sorted(entries, key=lambda e: e.get("view_count") or 0, reverse=True)[:n]


def resolve(handle, n):
    r = subprocess.run([*YT, "--no-update", "-J", "--flat-playlist", "--playlist-end", str(SCAN), shorts_url(handle)],
                       capture_output=True, text=True)
    entries = json.loads(r.stdout).get("entries", []) if r.returncode == 0 and r.stdout else []
    if not entries:
        sys.exit(f"{handle} has no YouTube Shorts to list.")
    return [e["url"] for e in top_by_views(entries, n)]


def cuts(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", "select='gt(scene,0.25)',metadata=print", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return err.count("pts_time")


def seconds(path):  # measured: yt-dlp gives no duration for Instagram
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


def study(url, out):
    info = subprocess.run([*YT, "--no-update", "--no-playlist", "--max-filesize", "300M", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
                           "--merge-output-format", "mp4", "-o", os.path.join(out, "%(id)s.%(ext)s"), "--print", "after_move:%()j",
                           "--no-simulate", "-q", "--no-warnings", url], capture_output=True, text=True)
    if info.returncode or not info.stdout.strip():
        print(f"  skipped {url}: {info.stderr.strip()[-200:]}")
        return None
    meta = json.loads(info.stdout.strip().splitlines()[-1])
    path = os.path.join(out, f"{meta['id']}.mp4")
    r = subprocess.run([sys.executable, os.path.join(HERE, "reference_study.py"), path, "--out", os.path.join(out, meta["id"])],
                       capture_output=True, text=True)
    log = os.path.exists(os.path.join(out, meta["id"], "edit-log.txt"))
    if not log:  # the sheet and frames are written first, so the study still works by eye
        print(f"  {meta['id']}: no Gemini edit log, read the sheet ({r.stderr.strip()[-120:]})")
    dur, c = seconds(path), cuts(path)
    return {"id": meta["id"], "url": url, "title": meta.get("title"), "uploader": meta.get("uploader"), "views": meta.get("view_count"),
            "seconds": round(dur, 1), "cuts": c, "cuts_per_min": round(c / dur * 60, 1), "edit_log": log}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--youtube", action="store_true", help="resolve @handle on YouTube")
    a = ap.parse_args()
    if any(shorts_url(s) for s in a.sources) and not a.youtube:
        sys.exit("a bare handle means Instagram, which can't be listed logged out: read reel links off the profile with the "
                 "Chrome tools, or ask the user for them, then pass the links. Use --youtube only if they said YouTube.")
    os.makedirs(a.out, exist_ok=True)
    urls = [u for s in a.sources for u in (resolve(s, a.n) if shorts_url(s) else [s])]
    reels = [r for r in (study(u, a.out) for u in urls) if r]
    if not reels:
        sys.exit("nothing could be fetched; try other links")
    json.dump({"sources": a.sources, "reels": reels}, open(os.path.join(a.out, "study.json"), "w"), indent=1, ensure_ascii=False)
    for r in reels:
        print(f"{r['id']}  {r['seconds']:.0f} s  {r['cuts_per_min']} cuts/min  {r['views']} views  {r['title']}")


if __name__ == "__main__":
    main()
