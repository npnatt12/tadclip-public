#!/usr/bin/env bash
# One-shot setup on a Mac with Homebrew: installs what TadClip needs, then runs doctor.sh. Safe to re-run.
#   bash scripts/setup.sh
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
say() { echo; echo "== $1"; }
[ "$S" -ef "$HOME/.claude/skills/tadclip" ] || echo "WARNING: TadClip belongs in ~/.claude/skills/tadclip (some scripts look for their face models there). This copy is in $S."
command -v brew >/dev/null || { echo "Homebrew is missing: install it from https://brew.sh (it needs your password), then re-run."; exit 1; }

say "tools (ffmpeg, Node 22, uv)"
command -v ffmpeg >/dev/null || brew install ffmpeg
[ -x /opt/homebrew/opt/node@22/bin/node ] || brew install node@22
command -v uv >/dev/null || brew install uv

say "python packages"
PK="numpy opencv-python pillow google-genai"
python3 -c "import numpy, cv2, PIL, google.genai" 2>/dev/null || python3 -m pip install -q --user $PK || python3 -m pip install -q --user --break-system-packages $PK
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
