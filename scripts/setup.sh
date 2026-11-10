#!/usr/bin/env bash
# One-shot setup on a Mac: installs what TadClip needs, then runs doctor.sh. Safe to re-run.
# Everything goes in your home folder (~/.local), so it never asks for your Mac password or Apple's developer tools.
#   bash scripts/setup.sh
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
# before each step: wait out a dropped connection instead of failing every download in it (up to 15 min)
waitnet() { local i=0; until curl -fsI -m 10 https://pypi.org >/dev/null 2>&1; do
  [ $i = 0 ] && echo "No internet right now. Waiting for it to come back... (ไม่มีอินเทอร์เน็ต กำลังรอ)"; i=$((i+1)); [ $i -ge 90 ] && return 1; sleep 10; done; }
N=0; say() { N=$((N+1)); echo; echo "== [$N/8] $1"; waitnet; }    # progress the user (or the agent relaying it) can see
[ "$S" -ef "$HOME/.claude/skills/tadclip" ] || echo "WARNING: TadClip belongs in ~/.claude/skills/tadclip (some scripts look for their face models there). This copy is in $S."
BIN="$HOME/.local/bin"; T="$HOME/.local/share/tadclip-tools"; mkdir -p "$BIN" "$T"
export PATH="$BIN:$PATH"
# uv looks for a python on PATH; without Apple's developer tools, running /usr/bin/python3 just opens their install
# window. Only uv's own pythons, then: here, and in every later session on such a Mac (creator_study.py runs uv too)
export UV_PYTHON_PREFERENCE=only-managed
xcode-select -p >/dev/null 2>&1 || for f in .zshenv .zprofile; do grep -qs UV_PYTHON_PREFERENCE "$HOME/$f" || echo 'export UV_PYTHON_PREFERENCE=only-managed  # TadClip' >> "$HOME/$f"; done
# the key file for the optional keys (Gemini, Pexels): TadClip works without them
[ -e "$S/.env" ] || cp "$S/.env.example" "$S/.env"; chmod 600 "$S/.env"
# fetch URL SHA256 FILE: download, refuse it if the checksum differs
# every download gives up on a stalled connection (under 1 KB/s for a minute) and tries again: a dead link once hung an
# install for 20 min with no message (11-09 rehearsal)
C="--retry 5 --retry-all-errors --connect-timeout 20 --speed-limit 1024 --speed-time 60"
fetch() { curl -fsSL $C "$1" -o "$3" && echo "$2  $3" | shasum -a 256 -c -s || { echo "download failed or changed: $1"; rm -f "$3"; return 1; }; }

say "tools: uv, Node 22, ffmpeg (~150 MB)"
# uv: Astral's GitHub release, pinned and checked like Node and ffmpeg below (11-09: releases.astral.sh, where their install
# script points, sent 0 bytes for minutes while GitHub was fine); their script only if GitHub fails
UVV=0.11.6
command -v uv >/dev/null || { fetch "https://github.com/astral-sh/uv/releases/download/$UVV/uv-aarch64-apple-darwin.tar.gz" 4b69a4e366ec38cd5f305707de95e12951181c448679a00dce2a78868dfc9f5b "$T/uv.tgz" &&
  tar -xzf "$T/uv.tgz" -C "$BIN" --strip-components 1 && rm "$T/uv.tgz"; } ||
  { curl -LsSf $C https://astral.sh/uv/install.sh > "$T/uv-install.sh" && sh "$T/uv-install.sh"; }    # Astral's own installer, into ~/.local/bin
# ~/.local/bin on PATH for every new Terminal and agent session. .zprofile runs after macOS's path_helper (which
# moves /usr/bin first), so our python3 wins there too; .zshenv covers non-login shells
for f in .zshenv .zprofile; do grep -qs 'HOME/.local/bin' "$HOME/$f" || echo 'export PATH="$HOME/.local/bin:$PATH"  # TadClip' >> "$HOME/$f"; done
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

# venv DIR REQS: make it if missing, then install the pinned set (uv downloads in parallel). Re-runs pick up a half-made venv.
venv() { [ -x "$1/bin/python" ] || uv venv -q -p 3.11 "$1"; uv pip install --python "$1/bin/python" -r "$2"; }

say "Python packages in ~/.venvs/media (~400 MB)"
# never the Mac's own python3 (Xcode's 3.9 + pip 21 can backtrack for half an hour): a uv venv with the pinned set
M="$HOME/.venvs/media"
"$M/bin/python" -c "import numpy, cv2, PIL, google.genai" 2>/dev/null || venv "$M" "$S/scripts/venvs/media.txt"
# the scripts run as python3: point it at the venv unless python3 already has the packages. Probing /usr/bin/python3
# without Apple's developer tools opens their install window, so only probe when they're there
xcode-select -p >/dev/null 2>&1 && python3 -c "import numpy, cv2, PIL, google.genai" 2>/dev/null ||
  { rm -f "$BIN/python3"; printf '#!/bin/sh\nexec "%s/bin/python" "$@"\n' "$M" > "$BIN/python3"; chmod +x "$BIN/python3"; }    # a wrapper, not a symlink: the venv only counts when its own path runs

say "English transcription: whisper (~300 MB)"
command -v whisper >/dev/null || uv tool install -p 3.11 openai-whisper

say "Thai transcription in ~/.venvs/mlxw (~300 MB, the longest step: up to 20 min)"
V="$HOME/.venvs/mlxw"
"$V/bin/python" -c "import mlx_whisper, pythainlp" 2>/dev/null || venv "$V" "$S/scripts/venvs/mlxw.txt"
# the Whisper model too (1.5 GB), now and not during the first reel (11-09: +20 min mid-run on a fresh account)
say "Thai transcription model (~1.5 GB)"
"$V/bin/python" -c "from huggingface_hub import snapshot_download as d; d('mlx-community/whisper-large-v3-turbo')" >/dev/null 2>&1 ||
  echo "MISS whisper model: the first clip would download it (paste the install line again to retry)"

say "sound effects, music, emoji (~200 MB)"
python3 "$S/scripts/library_restore.py" --licensed-only

say "agents (Claude Code, Codex) and the TadClip app"
mkdir -p "$HOME/.claude/agents"
cp "$S/templates/agents/reel-helper.md" "$HOME/.claude/agents/"    # overwrite: updates to the helper must reach it
if [ -d "$HOME/.codex" ]; then
  mkdir -p "$HOME/.codex/skills"
  [ -e "$HOME/.codex/skills/tadclip" ] || ln -s "$S" "$HOME/.codex/skills/tadclip"
  echo "Codex: linked as ~/.codex/skills/tadclip"
fi
TADCLIP_NO_START=1 bash "$S/app/install.sh"    # ~/TadClip with the TadClip.app inside; started below, once the check passes

say "check"
bash "$S/scripts/doctor.sh" | tee "$T/doctor.log"
# one machine-readable last line, so an agent can loop "run again until ok" without reading prose
m=$(sed -n 's/.* \([0-9][0-9]*\) missing$/\1/p' "$T/doctor.log" | tail -1)
# all there: start the app (it opens its page now and at every login); on an update this restarts it on the new code
if [ "${m:-1}" = 0 ] && [ -z "${TADCLIP_NO_START:-}" ] && [ -f "$HOME/Library/LaunchAgents/com.tadclip.app.plist" ]; then
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.tadclip.app.plist" 2>/dev/null || launchctl kickstart -k "gui/$(id -u)/com.tadclip.app"
  echo "TadClip app: the page opens in your browser (http://127.0.0.1:4747/)"
fi
[ "${m:-1}" = 0 ] && { echo "TADCLIP_STATUS=ok"; exit 0; }
echo "TADCLIP_STATUS=incomplete ${m:-?} missing (safe to run again: it skips what's done)"; exit 1
