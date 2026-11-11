#!/usr/bin/env bash
# Optional: the small venv for scripts/font_metrics.py, which regenerates scripts/lib/metrics.json (the glyph widths the
# caption templates lay out with) after a font is added to templates/fonts. The caption templates themselves need nothing.
#   bash scripts/setup_captions.sh            -> ~/.venvs/tadclip-captions (override with CAPTIONS_VENV=/path)
set -euo pipefail
V="${CAPTIONS_VENV:-$HOME/.venvs/tadclip-captions}"
case "$(uname -s)" in MINGW* | MSYS* | CYGWIN*) VB="$V/Scripts" ;; *) VB="$V/bin" ;; esac   # a venv's programs: Scripts\ on Windows
PY="${PYTHON311:-$(command -v python3.11 || command -v python3)}"
[ -x "$VB/python" ] || "$PY" -m venv "$V"
"$VB/pip" install -q --upgrade pip
"$VB/pip" install -q "fonttools==4.66.1" "brotli==1.2.0"
"$VB/python" -c "import fontTools, brotli" && echo "captions venv ready: $V"
