#!/usr/bin/env bash
# Check everything tadclip needs on this machine, and say how to fix what's missing.
#   bash scripts/doctor.sh
S="$(cd "$(dirname "$0")/.." && pwd)"
. "$S/scripts/lib/plat.sh"   # TC_WIN, vpy (a venv's python), THAI_* (this OS's Thai speech engine)
ok=0; bad=0
pass() { echo "  ok    $1"; ok=$((ok+1)); }
fail() { echo "  MISS  $1  ->  $2"; bad=$((bad+1)); }

# numpy/opencv/google-genai may live in a separate venv (MEDIA_PY, or ~/.venvs/media) on machines whose python3 has none
PY=${MEDIA_PY:-python3}; "$PY" -c "import numpy" 2>/dev/null || { [ -x "$(vpy "$HOME/.venvs/media")" ] && PY="$(vpy "$HOME/.venvs/media")"; }

echo "tools"
# setup.sh puts uv, whisper, node, ffmpeg and the python3 wrapper in ~/.local/bin, and that folder on PATH (.zshenv, .zprofile)
case ":$PATH:" in *":$HOME/.local/bin:"*) [ -d "$HOME/.local/bin" ] && pass "~/.local/bin on PATH";;
  # the desktop app keeps the PATH it was opened with, so its sessions miss the install until it restarts (11-09 report):
  # not a fault. Each command adds the folder itself (SKILL.md step 0); restarting the app makes it stick
  *) [ -d "$HOME/.local/bin" ] && echo "  note  ~/.local/bin is not on this app's PATH yet: added for these commands. Quit and reopen the Claude app once to make it stick (ปิดแล้วเปิดแอป Claude ใหม่หนึ่งครั้ง)"
     export PATH="$HOME/.local/bin:$PATH";; esac
command -v ffmpeg >/dev/null && pass "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')" || fail ffmpeg "bash $S/scripts/setup.sh"
ffmpeg -hide_banner -buildconf 2>/dev/null | grep -q enable-libvpx && pass "ffmpeg libvpx (alpha WebM memes)" || fail "ffmpeg libvpx" "bash $S/scripts/setup.sh"
ffmpeg -hide_banner -buildconf 2>/dev/null | grep -q enable-libass && pass "ffmpeg libass" || fail "ffmpeg libass" "bash $S/scripts/setup.sh"
[ -x /opt/homebrew/opt/node@22/bin/node ] && export PATH="/opt/homebrew/opt/node@22/bin:$PATH"  # same as hf.sh
command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] && pass "node $(node -v)" || fail "node >= 22 (HyperFrames)" "bash $S/scripts/setup.sh"
command -v uv >/dev/null && pass "uv (creator_study.py runs the latest yt-dlp through it)" || fail "uv (creator_study.py: an old yt-dlp gets 403 from YouTube)" "bash $S/scripts/setup.sh"
"$THAI_PY" -c "import $THAI_MOD" 2>/dev/null && pass "${THAI_MOD//_/-} (${THAI_VENV/#$HOME/~}, Thai word times)" || fail "${THAI_MOD//_/-} (ClubGig's Thai word times)" "bash $S/scripts/setup.sh"
"$THAI_PY" -c "from huggingface_hub import snapshot_download as d; d('$THAI_REPO', local_files_only=True)" >/dev/null 2>&1 &&
  pass "whisper model downloaded (large-v3-turbo)" || fail "whisper model (the first clip would download 1.5 GB mid-run)" "bash $S/scripts/setup.sh"
# HyperFrames is pinned in ONE place (scripts/HF_VERSION), read by hf.sh, hf_version.py and build.mjs
hv=$(cat "$S/scripts/HF_VERSION" 2>/dev/null)
v=$(bash "$S/scripts/hf.sh" --version 2>/dev/null | tail -1)
[ -n "$v" ] && [ "$v" = "${HF_VERSION:-$hv}" ] && pass "hyperframes $v (pinned in scripts/HF_VERSION)" || fail "hyperframes $hv (scripts/HF_VERSION)" "bash $S/scripts/hf.sh --version (needs network once)"
[ -n "$HF_VERSION" ] && [ "$HF_VERSION" != "$hv" ] && echo "  WARN  HF_VERSION=$HF_VERSION overrides scripts/HF_VERSION ($hv): renders here differ from the other machine; unset it after the test"
un=$(grep -rnE 'npx (-y )?hyperframes([^@]|$)|"npx", "hyperframes"' "$S" --include='*.md' --include='*.py' --include='*.sh' --include='*.mjs' --include='*.js' 2>/dev/null | grep -v -e '/public/' -e node_modules -e '/docs/HANDOFF-' | grep -iv -e unpinned -e 'instead of')
[ -z "$un" ] && pass "no unpinned hyperframes calls in the skill" || { echo "  WARN  unpinned hyperframes calls (use \$S/scripts/hf.sh, or hf() from scripts/hf_version.py):"; echo "$un" | sed 's/^/          /'; }
# x264's thread count is pinned in ONE place (scripts/X264_THREADS): on automatic threads it follows the core count and
# each Mac writes different bytes. Every libx264 encode passes it right after libx264; HyperFrames' get it from hf_ffmpeg.sh.
# VideoToolbox's encoder gives different bytes on every run, so no script may use it.
xt=$(cat "$S/scripts/X264_THREADS" 2>/dev/null)
ux=$(grep -rnIE --include='*.py' --include='*.sh' --include='*.mjs' --include='*.js' -- "(-c:v|-vcodec|-codec:v)[\"', ]*(libx264|h264_videotoolbox|hevc_videotoolbox)" "$S" 2>/dev/null \
  | grep -v -e node_modules -e '/\.venv' -e '/scripts/doctor.sh:' | grep -vE -- "libx264[\"', ]*-threads.{0,60}X264_THREADS")
# Windows: HyperFrames runs the compiled twin, hf_ffmpeg.exe (built by setup.sh from hf_ffmpeg.cs), so that's the one checked
if [ -n "$TC_WIN" ]; then hx=$(HF_REAL_FFMPEG="$(cygpath -w "$(type -P echo)")" "$S/scripts/hf_ffmpeg.exe" -i in.mp4 -c:v libx264 -preset medium out.mp4 2>/dev/null | tr -d '\r')
else hx=$(HF_REAL_FFMPEG=echo bash "$S/scripts/hf_ffmpeg.sh" -i in.mp4 -c:v libx264 -preset medium out.mp4 2>/dev/null); fi
[ -n "$xt" ] && [ -z "$ux" ] && [ "$hx" = "-i in.mp4 -c:v libx264 -threads $xt -preset medium out.mp4" ] \
  && pass "every libx264 encode uses -threads $xt (scripts/X264_THREADS), HyperFrames' too (hf_ffmpeg.sh)" \
  || { echo "  WARN  x264 threads not pinned: these encodes give different bytes on each Mac (pass -threads from scripts/X264_THREADS right after libx264; no VideoToolbox encoder):"
       [ -z "$xt" ] && echo "          scripts/X264_THREADS is missing or empty"
       [ "$hx" = "-i in.mp4 -c:v libx264 -threads $xt -preset medium out.mp4" ] || echo "          scripts/hf_ffmpeg.sh does not add it to HyperFrames' encodes"
       [ -n "$ux" ] && echo "$ux" | sed 's/^/          /'; }
w=${WHISPER:-$(command -v whisper)}; [ -n "$w" ] && pass "whisper ($w)" || fail whisper "pip install openai-whisper (or set WHISPER=/path)"
command -v yt-dlp >/dev/null && pass "yt-dlp $(yt-dlp --version)" || echo "  opt   yt-dlp not installed: only needed to pull a reference video from a link -> brew install yt-dlp"
"$PY" -c "import numpy" 2>/dev/null && pass "python numpy ($PY)" || fail numpy "pip install numpy"
"$PY" -c "import cv2; cv2.FaceDetectorYN" 2>/dev/null && pass "python opencv (face tracking)" || fail opencv "pip install opencv-python"
"$PY" -c "import google.genai" 2>/dev/null && pass "python google-genai" || fail "python google-genai (B-roll people/line checks, QA)" "$PY -m pip install google-genai"
"$PY" -c "import PIL" 2>/dev/null && pass "python pillow" || fail pillow "$PY -m pip install pillow"

echo "keys"
# required: insert_prep.py, broll_vision.py and broll_qa.py's people / match checks ask Gemini, and an unchecked shot FAILS
# the render's QA. One cheap call proves the key works (a set but revoked key looks fine until the batch).
if [ -n "$GEMINI_API_KEY" ] || grep -qs '^GEMINI_API_KEY=.' "$S/.env"; then
  r=$(S="$S" "$PY" - 2>&1 <<'PYEOF'
import os, re
from google import genai
from google.genai import types
k = os.environ.get("GEMINI_API_KEY")
if not k:
    m = re.search(r"GEMINI_API_KEY[ \t]*=[ \t]*['\"]?([^'\"\n]+)", open(os.path.join(os.environ["S"], ".env")).read())
    k = m.group(1).strip()
c = genai.Client(api_key=k, http_options=types.HttpOptions(timeout=30000))
print((c.models.generate_content(model="gemini-flash-latest", contents="Reply with the single word ok.").text or "").strip()[:20])
PYEOF
)
  case "$r" in [Oo]k*) pass "GEMINI_API_KEY works (one test call)";;
    # any Google-side 5xx is Google's trouble, not a missing install (11-11: a 504 made ready.sh say "not ready")
    *503*|*UNAVAILABLE*|*DEADLINE_EXCEEDED*|*ServerError*) pass "GEMINI_API_KEY set; Google is busy (server error), so the key is untested: run this again later";;
    *429*|*RESOURCE_EXHAUSTED*) pass "GEMINI_API_KEY works, but today's free quota is used up (429): Gemini steps wait for the reset";;
    *ConnectError*|*nodename*|*"Errno 8"*|*Timeout*|*"timed out"*|*"Network is unreachable"*) fail "GEMINI_API_KEY set, but Google can't be reached (no internet?), so the key is untested" "check the internet connection, then run this again";;
    *) r=${r##*$'\n'}; fail "GEMINI_API_KEY is set but the test call failed: ${r:0:140}" "check the key at aistudio.google.com/apikey (env or $S/.env)";; esac
else echo "  opt   GEMINI_API_KEY not set: reels work without it (Thai text from whisper, pictures picked by eye, no B-roll vision check). More tailored with a free key -> $S/.env (docs/INSTALL.md, step 3)"; fi

if [ -n "$PEXELS_API_KEY" ] || grep -qs '^PEXELS_API_KEY=.' "$S/.env" "$S/.env.local"; then pass "PEXELS_API_KEY (ClubGig stock)"; else echo "  opt   PEXELS_API_KEY not set: stock search falls back to Wikimedia Commons (fewer, smaller clips), photos too. More choice with a free key -> $S/.env (docs/INSTALL.md, step 3)"; fi
if [ -n "$ELEVENLABS_API_KEY" ] || grep -qs '^ELEVENLABS_API_KEY=.' "$S/.env"; then pass "ELEVENLABS_API_KEY (narrated explainers)"; else echo "  opt   ELEVENLABS_API_KEY not set: only scripts/tts_elevenlabs.py (explainer voiceover) needs it -> $S/.env"; fi
{ [ -x "${DF_VENV:-$S/.venv-df}/bin/deepFilter" ] || [ -x "${DF_VENV:-$S/.venv-df}/Scripts/deepFilter.exe" ]; } && pass "DeepFilterNet (scripts/denoise.sh)" || echo "  opt   DeepFilterNet not set up: scripts/denoise.sh installs it on first use (needs python3.11 + uv)"

echo "optional tools (the core skill works without them)"
# ฟัง on the page reads the screen aloud with a Thai voice: macOS has Kanya built in; Windows only after its Thai speech
# pack (admin). Edge's online voices may cover it; unconfirmed (CI's headless Edge on Windows Server listed none, 11-11)
if [ -n "$TC_WIN" ]; then
  tv=$(powershell.exe -NoProfile -NonInteractive -Command "[void][Windows.Media.SpeechSynthesis.SpeechSynthesizer,Windows.Media,ContentType=WindowsRuntime]; ([Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object Language -like 'th*' | Select-Object -First 1).DisplayName" 2>/dev/null | tr -d '\r')
  [ -n "$tv" ] && pass "Thai voice for ฟัง ($tv)" || echo "  opt   no Thai voice in Windows: ฟัง (read aloud) may stay silent. Add one: Settings > Time & language > Speech > Add voices > ไทย (asks for admin; Edge may offer an online Thai voice without it)"
fi
[ -f "$S/templates/vendor/hf-paper.js" ] && pass "Paper Shaders bundle (templates/vendor/hf-paper.js)" || fail "templates/vendor/hf-paper.js (shader looks)" "git checkout templates/vendor, or rebuild: cd $S/tools/paper && npm install && node build-vendor.mjs"
e=$(ls "$S"/library/emoji/*.webm 2>/dev/null | wc -l | tr -d ' ')
[ "$e" -ge 30 ] && pass "animated emoji ($e Fluent webm)" || echo "  opt   animated emoji not fetched: emoji beats fall back to the font glyph -> python3 -I $S/scripts/emoji_fetch.py (needs ffmpeg libvpx-vp9)"
l=$(ls "$S"/library/luts/*.cube 2>/dev/null | wc -l | tr -d ' ')
[ "$l" -ge 6 ] && pass "film-look LUTs ($l in library/luts)" || echo "  opt   film-look LUTs not generated: only look.film needs them -> bash $S/scripts/setup_looks.sh (venv ~/.venvs/tadclip-looks)"
[ -x "$(vpy "${MATTE_VENV:-$HOME/.venvs/tadclip-matte}")" ] && pass "BiRefNet matte (behind beats, cutout beats)" || echo "  opt   BiRefNet matte not set up: behind beats fall back to hyperframes remove-background (u2net), cutout beats need it -> bash $S/scripts/setup_matte.sh (~2.6 GB with weights)"
mc="${CUTOUT_FX_CACHE:-${TADCLIP_MATTE_CACHE:-$HOME/.cache/tadclip-matte}}"
[ -x "$(vpy "${MATTE_VENV:-$HOME/.venvs/tadclip-matte}")" ] && [ ! -f "$mc/hf/BiRefNet_lite/model.safetensors" ] && echo "  opt   BiRefNet_lite weights not cached: cutout beats will download them (176 MB) on first use -> bash $S/scripts/setup_matte.sh"
[ -x "$(vpy "${AUDIOQA_VENV:-$HOME/.venvs/tadclip-audioqa}")" ] && pass "audio QA venv (vad_pauses, voice_enhance)" || echo "  opt   audio QA venv not set up: only autocut --vad, vad_pauses.py and voice_enhance.py need it -> bash $S/scripts/setup_audioqa.sh"
[ -x "$(vpy "${CAPTIONS_VENV:-$HOME/.venvs/tadclip-captions}")" ] && pass "caption metrics venv (scripts/font_metrics.py)" || echo "  opt   caption metrics venv not set up: only needed to add a font to the caption templates -> bash $S/scripts/setup_captions.sh"

echo "recipes"
ls "$S"/templates/fonts/inter-tight-cyrillic.woff2 "$S"/templates/fonts/playfair-display-italic-cyrillic.woff2 >/dev/null 2>&1 && pass "Seoul list / RESULT fonts (Inter Tight, Playfair Display, OFL)" || fail "templates/fonts/inter-tight-*.woff2" "git -C $S checkout templates/fonts"
miss=""; for e in waving-hand hand-splayed point-right running yum eyes fire; do [ -f "$S/library/emoji/$e.webm" ] || miss="$miss,$e"; done
[ -z "$miss" ] && pass "Seoul list emoji (hands, eyes, runner, yum, fire)" || echo "  opt   Seoul list emoji missing (${miss#,}) -> python3 -I $S/scripts/emoji_fetch.py --only ${miss#,}"
[ -f "$S/library/sfx/send-swoosh.wav" ] && pass "Seoul list send sound (send-swoosh)" || echo "  opt   send-swoosh not fetched (Seoul list outro) -> python3 $S/scripts/sfx_fetch.py --only send-swoosh"

echo "library"
n=$(ls "$S"/library/sfx/*.wav 2>/dev/null | wc -l | tr -d ' ')
[ "$n" -ge 30 ] && pass "sfx kit ($n files)" || fail "sfx kit ($n files)" "python3 $S/scripts/library_restore.py --sfx-only"
m=$(ls "$S"/library/memes/*/clip.webm "$S"/library/memes/*/image.png 2>/dev/null | wc -l | tr -d ' ')
if [ "$m" -ge 1 ]; then pass "memes ($m)"
elif [ -f "$S/.public-edition" ]; then echo "  opt   memes: none (public edition; add clips you have rights to with scripts/meme_add.py)"
else fail "memes" "python3 $S/scripts/library_restore.py --memes-only"; fi
ls "$S"/library/music/*.mp3 >/dev/null 2>&1 && pass "music beds" || fail "music beds" "python3 $S/scripts/library_restore.py --music-only"

echo "toolchain vs the other machine (scripts/toolchain.py: records this one in library/toolchain/, compares)"
tc=$(python3 "$S/scripts/toolchain.py" compare 2>&1); tcr=$?
echo "$tc" | sed -e 's/^  DIFF /  WARN  /' -e 's/^  info /  info  /' -e 's/^vs /  /' -e 's/^no other/  opt   no other/'
[ "$tcr" -ne 0 ] && echo "        the WARN lines change the edit (cut, mix or render); align them (docs/SYNC.md, Toolchain parity)"

echo; echo "$ok ok, $bad missing"
[ "$bad" -eq 0 ]
