"""The one HyperFrames CLI version every script lints, snapshots and renders with.

The version lives in scripts/HF_VERSION (one line). An HF_VERSION environment variable overrides it for a one-off test
(doctor.sh warns while it is set). Unpinned `npx hyperframes` fetches whatever was published last, so two machines,
or one machine on two days, render the same reel differently, and a release whose tarball 404s fails a whole batch.

    from hf_version import VERSION, hf
    subprocess.run(hf("render", "-o", out), cwd=project)       # ["npx", "-y", "hyperframes@<VERSION>", "render", ...]

Importing this also points HyperFrames at scripts/hf_ffmpeg.sh (HYPERFRAMES_FFMPEG_PATH, unless already set), which
fixes the audio mix's input order so the same reel gets the same audio on every render (why: hf_mix_order.py).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "HF_VERSION")
PINNED = open(FILE).read().strip()
VERSION = os.environ.get("HF_VERSION") or PINNED
WIN = sys.platform == "win32"
# Windows can't run hf_ffmpeg.sh as a program: its compiled twin (setup.sh builds hf_ffmpeg.exe), else the plain ffmpeg
os.environ.setdefault("HYPERFRAMES_FFMPEG_PATH", (os.path.join(HERE, "hf_ffmpeg.exe") if os.path.exists(os.path.join(HERE, "hf_ffmpeg.exe"))
                      else shutil.which("ffmpeg") or "ffmpeg") if WIN else os.path.join(HERE, "hf_ffmpeg.sh"))
if os.path.exists("/opt/homebrew/opt/node@22/bin/node"):  # HyperFrames needs Node >= 22, same as hf.sh
    os.environ["PATH"] = "/opt/homebrew/opt/node@22/bin:" + os.environ["PATH"]


def npx():
    """npx as a program list: Windows' npx is npx.cmd, which a list-form subprocess can't start, so node runs npm's own
    npx-cli.js (next to node.exe in the official Windows build)"""
    if not WIN: return ["npx"]
    node = shutil.which("node"); cli = os.path.join(os.path.dirname(node), "node_modules", "npm", "bin", "npx-cli.js") if node else ""
    return [node, cli] if os.path.exists(cli) else ["npx.cmd"]


def hf(*args):
    return [*npx(), "-y", f"hyperframes@{VERSION}", *args]
