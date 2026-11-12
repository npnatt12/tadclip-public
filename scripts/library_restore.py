#!/usr/bin/env python3
"""Rebuild the media the repo does not track (it keeps only manifests):
music beds from library/music/manifest.json (FreePD CC0 tracks: "url", else "mirror"/"mirror2", checked against "sha256"),
the private build's rip SFX (sfx_fetch.KIT; TadClip's own and the CC0 sounds are committed), every meme from its meta.json source + args, and the
animated Fluent emoji (library/emoji/set.json, MIT, via emoji_fetch.py).
Existing files are kept.

    library_restore.py [--memes-only | --sfx-only | --music-only | --emoji-only] [--licensed-only]

--licensed-only is the public build: CC0 music + Fluent emoji only (the SFX are in git), no
YouTube meme-sound rips and no meme clips. Film LUTs (library/luts) are generated,
not downloaded: bash scripts/setup_looks.sh.
"""
import argparse
import json
import re
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "library")


def sha256(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--memes-only", action="store_true")
    ap.add_argument("--sfx-only", action="store_true")
    ap.add_argument("--music-only", action="store_true")
    ap.add_argument("--emoji-only", action="store_true")
    ap.add_argument("--licensed-only", action="store_true", help="skip rip SFX and memes (public build)")
    a = ap.parse_args()
    bad = 0
    # animated emoji (Microsoft Fluent, MIT): fetched + converted to VP9-alpha WebM; resumable, existing items kept
    if not (a.memes_only or a.sfx_only or a.music_only):
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "emoji_fetch.py")])
        print(("ok   " if r.returncode == 0 else "FAIL ") + "emoji (library/emoji)")
        bad += r.returncode != 0
        if a.emoji_only:
            sys.exit(1 if bad else 0)
    if not os.path.isdir(os.path.join(LIB, "luts")) or not any(f.endswith(".cube") for f in os.listdir(os.path.join(LIB, "luts"))):
        print("note film LUTs (library/luts) are generated, not downloaded: bash scripts/setup_looks.sh (optional, film looks only)")
    # music beds: licensed files are downloaded from their source, never stored in git
    if not a.memes_only and not a.sfx_only:
        man = json.load(open(os.path.join(LIB, "music", "manifest.json")))
        for mid, m in man.items():
            dst = os.path.join(LIB, "music", m["file"])
            if os.path.exists(dst):
                continue
            urls = [u for u in (m.get("url"), m.get("mirror"), m.get("mirror2")) if u]
            if not urls:
                print(f"FAIL music {mid}: no download url in the manifest")
                bad += 1
                continue
            ok = False
            for url in urls:   # our own release, then archive.org's FreePD copy, then the archived freepd.com file
                r = subprocess.run(["curl", "-sfL", "--retry", "3", "--retry-all-errors", "--retry-delay", "3", "-A", "Mozilla/5.0", "-o", dst, url])
                ok = r.returncode == 0 and os.path.exists(dst) and (not m.get("sha256") or sha256(dst) == m["sha256"])
                if ok:
                    break
                if os.path.exists(dst):
                    os.remove(dst)  # never keep an error page or a changed file posing as the track
            print(("ok   " if ok else "FAIL ") + "music " + mid)
            bad += not ok
    if a.music_only:
        sys.exit(1 if bad else 0)
    if not a.memes_only:
        if a.licensed_only:
            print("ok   sfx (TadClip's own + CC0, in git: nothing to download)")
        else:   # the private build's rips
            bad += subprocess.run([sys.executable, os.path.join(HERE, "sfx_fetch.py")]).returncode != 0
    if a.licensed_only:
        print("skip memes (--licensed-only: meme clips are unlicensed rips)")
    elif not a.sfx_only:
        mdir = os.path.join(LIB, "memes")
        for d in sorted(os.listdir(mdir)):
            p = os.path.join(mdir, d, "meta.json")
            if not os.path.exists(p):
                continue
            m = json.load(open(p))
            g = m.get("args", {})
            cmd = [sys.executable, os.path.join(HERE, "meme_add.py"), d, m["source_url"], "--tags", ",".join(m["emotion"]),
                   "--use", m["use_case"], "--triggers", ",".join(m["trigger_phrases"]), "--trend", m["trend_status"], "--name", m["name"]]
            for k, flag in (("in", "--in"), ("out", "--out"), ("key", "--key"), ("similarity", "--similarity"), ("w", "--w"), ("crop", "--crop")):
                if k in g:
                    cmd += [flag, str(g[k])]
            if g.get("no_audio"):
                cmd.append("--no-audio")
            if m.get("sfx") and not m.get("image"):
                cmd += ["--sfx", m["sfx"]]
            elif m.get("image"):
                cmd += ["--sfx", m.get("sfx", "vine-boom")]
            r = subprocess.run(cmd, capture_output=True, text=True)
            print(("ok   " if r.returncode == 0 else "FAIL ") + d + ("" if r.returncode == 0 else ": " + r.stderr[-300:]))
            bad += r.returncode != 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
