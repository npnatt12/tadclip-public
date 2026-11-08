#!/usr/bin/env bash
# One-shot setup on a Mac: installs what TadClip needs, then runs doctor.sh. Safe to re-run.
# Everything goes in your home folder (~/.local), so it never asks for your Mac password or Apple's developer tools.
#   bash scripts/setup.sh
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
say() { echo; echo "== $1"; }
[ "$S" -ef "$HOME/.claude/skills/tadclip" ] || echo "WARNING: TadClip belongs in ~/.claude/skills/tadclip (some scripts look for their face models there). This copy is in $S."
BIN="$HOME/.local/bin"; T="$HOME/.local/share/tadclip-tools"; mkdir -p "$BIN" "$T"
export PATH="$BIN:$PATH"
# fetch URL SHA256 FILE: download, refuse it if the checksum differs
fetch() { curl -fsSL "$1" -o "$3" && echo "$2  $3" | shasum -a 256 -c -s || { echo "download failed or changed: $1"; rm -f "$3"; return 1; }; }

say "tools (uv, Python, Node 22, ffmpeg)"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh    # Astral's own installer, into ~/.local/bin
uv tool update-shell >/dev/null 2>&1 || true    # puts ~/.local/bin on PATH for new Terminal and agent sessions
# without Apple's developer tools, /usr/bin/python3 only opens their install window: give python3 a real one
xcode-select -p >/dev/null 2>&1 || [ -x "$BIN/python3" ] || { uv python install -q 3.11 && ln -sf "$(uv python find 3.11)" "$BIN/python3"; }
node -p 'process.versions.node.split(".")[0] >= 22 || process.exit(1)' >/dev/null 2>&1 || [ -x /opt/homebrew/opt/node@22/bin/node ] || {
  NV=v22.23.4    # nodejs.org's official build; checksum from its SHASUMS256.txt
  fetch "https://nodejs.org/dist/$NV/node-$NV-darwin-arm64.tar.gz" c9e1dbc748b33ed2d14f42445191ecaf14c56259c7a9a26d0042c49ec2b66428 "$T/node.tgz" &&
    rm -rf "$T/node" && mkdir "$T/node" && tar -xzf "$T/node.tgz" -C "$T/node" --strip-components 1 && rm "$T/node.tgz" &&
    for b in node npm npx; do ln -sf "$T/node/bin/$b" "$BIN/$b"; done
}
# ponytail: pinned static build (Martin Riedl, Developer ID signed + notarized, libass/libvpx/x264 in); bump FF + both sums together
ffmpeg -hide_banner -buildconf 2>/dev/null | grep -q enable-libass || {
  FF=https://ffmpeg.martin-riedl.de/download/macos/arm64/1789931890_9.0.2
  for p in "ffmpeg c8ed4c4e6978a03c485edbfe4e0a5dc2380f8a30bba5150531b31b094492d924" "ffprobe fcbe839537485eaee7a7a8bc5cbc0f90d53617e80943e8a5b2e31cb851197ea6"; do
    set -- $p; fetch "$FF/$1.zip" "$2" "$T/$1.zip" && unzip -oq "$T/$1.zip" -d "$BIN" && rm "$T/$1.zip"
  done
}

say "python packages"
PK="numpy opencv-python pillow google-genai"
python3 -c "import numpy, cv2, PIL, google.genai" 2>/dev/null || python3 -m pip install -q --user $PK || python3 -m pip install -q --user --break-system-packages $PK || uv pip install -q --python "$(command -v python3)" --break-system-packages $PK
command -v whisper >/dev/null || uv tool install openai-whisper

say "Thai transcription (~/.venvs/mlxw)"
V="$HOME/.venvs/mlxw"
"$V/bin/python" -c "import mlx_whisper" 2>/dev/null || { uv venv -q -p 3.11 "$V" && VIRTUAL_ENV="$V" uv pip install -q mlx-whisper; }

say "sound effects, music, emoji"
python3 "$S/scripts/library_restore.py" --licensed-only

say "agents (Claude Code, Codex)"
mkdir -p "$HOME/.claude/agents"
cp -n "$S/templates/agents/reel-helper.md" "$HOME/.claude/agents/" 2>/dev/null
if [ -d "$HOME/.codex" ]; then
  mkdir -p "$HOME/.codex/skills"
  [ -e "$HOME/.codex/skills/tadclip" ] || ln -s "$S" "$HOME/.codex/skills/tadclip"
  echo "Codex: linked as ~/.codex/skills/tadclip"
fi

say "key file"
[ -e "$S/.env" ] || cp "$S/.env.example" "$S/.env"
chmod 600 "$S/.env"
echo "Keys go in $S/.env. To open it: open -e \"$S/.env\". Links: docs/INSTALL.md, step 3."

say "check"
bash "$S/scripts/doctor.sh"
