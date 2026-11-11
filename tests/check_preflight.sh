#!/usr/bin/env bash
# setup.sh and install.sh stop in the first second on a Mac that can't run TadClip (Intel, macOS < 14, < 8 GB free)
# and go on for a supported one. Fake uname/sw_vers/df on PATH; a throwaway HOME; the good case is killed after 4 s.
set -u; S="$(cd "$(dirname "$0")/.." && pwd)"; W=$(mktemp -d "${TMPDIR:-/tmp}/tc-pre.XXXX"); fails=0
case_() { # name arch macos freeGB script expect
  mkdir -p "$W/$1/bin" "$W/$1/home"
  printf '#!/bin/sh\n[ "$1" = -m ] && echo %s || echo "Darwin %s"\n' "$2" "$2" > "$W/$1/bin/uname"
  printf '#!/bin/sh\necho %s\n' "$3" > "$W/$1/bin/sw_vers"
  printf '#!/bin/sh\necho "Filesystem 1K-blocks Used Available"; echo "x 0 0 %s"\n' "$(($4*1048576))" > "$W/$1/bin/df"
  chmod +x "$W/$1/bin/"*
  out=$(HOME="$W/$1/home" PATH="$W/$1/bin:$PATH" TADCLIP_SRC="$S" TADCLIP_NO_START=1 timeout 4 bash "$5" </dev/null 2>&1)
  if grep -q "$6" <<<"$out"; then echo "ok   $1"; else echo "FAIL $1: wanted '$6'"; echo "$out" | head -5; fails=1; fi
}
for s in "$S/scripts/setup.sh" "${INSTALL_SH:-}"; do [ -f "$s" ] || continue; echo "== $(basename "$s")"
  case_ intel x86_64 14.5 50 "$s" "TADCLIP_STATUS=unsupported"
  case_ old13 arm64 13.6 50 "$s" "TADCLIP_STATUS=unsupported"
  case_ full arm64 15.1 3 "$s" "TADCLIP_STATUS=no_space"
  case_ good arm64 15.1 50 "$s" "\[1/8\]\|TadClip from"
  rm -rf "$W"/*
done
rm -rf "$W"; exit $fails
