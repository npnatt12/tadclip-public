#!/usr/bin/env bash
# The pinned HyperFrames CLI: `$S/scripts/hf.sh render -o build/reel.mp4` = npx -y hyperframes@<scripts/HF_VERSION> ...
# An HF_VERSION environment variable overrides the file for a one-off test (doctor.sh warns while it is set).
# HyperFrames runs ffmpeg through hf_ffmpeg.sh, which fixes the audio mix's input order (why: hf_mix_order.py).
v="${HF_VERSION:-$(cat "$(dirname "$0")/HF_VERSION")}"
# local: HyperFrames needs Node >= 22; this machine's default is node@20, so use the side-installed node@22 keg
[ -x /opt/homebrew/opt/node@22/bin/node ] && export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)   # Windows (Git Bash): HyperFrames spawns ffmpeg as a program, so a .sh can't stand in; the
    # compiled twin hf_ffmpeg.exe (setup.sh builds it from hf_ffmpeg.cs) does the same two fixes, else the plain ffmpeg
    here="$(cd "$(dirname "$0")" && pwd)"
    if [ -x "$here/hf_ffmpeg.exe" ]; then d="$(cygpath -w "$here/hf_ffmpeg.exe")"; else d="$(cygpath -w "$(command -v ffmpeg)")"; fi
    export HYPERFRAMES_FFMPEG_PATH="${HYPERFRAMES_FFMPEG_PATH:-$d}" ;;
  *) export HYPERFRAMES_FFMPEG_PATH="${HYPERFRAMES_FFMPEG_PATH:-$(cd "$(dirname "$0")" && pwd)/hf_ffmpeg.sh}" ;;
esac
exec npx -y "hyperframes@$v" "$@"
