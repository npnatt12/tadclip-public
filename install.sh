#!/usr/bin/env bash
# TadClip in one line (Terminal, or pasted into Claude Code / Codex, which run it):
#   curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
# Safe to re-run: it updates what's already there and skips what's done. Every line it prints is also kept, with the
# time, in ~/Library/Logs/TadClip/install-<date>.log (scripts/logs.sh collects it for a bug report).
set -u
# all in functions, called on the last line: a half-downloaded script never runs, and nothing it runs can read the rest
# of the script from the pipe
main() {
  REPO=${TADCLIP_REPO:-npnatt12/tadclip-public}
  D="$HOME/.claude/skills/tadclip"
  t0=$(date +%s)

  echo "TadClip install · ติดตั้ง TadClip"
  echo "mac: $(sw_vers -productVersion 2>/dev/null) $(uname -m) · free disk: $(df -h "$HOME" | awk 'NR==2{print $4}') · user: $(whoami)"
  echo "agents: claude $(command -v claude >/dev/null && claude --version 2>/dev/null | head -1 || echo none) · codex $(command -v codex >/dev/null && echo yes || echo none)"
  [ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] || echo "Note: TadClip is built for Apple silicon Macs. It may not work here."

  # No Homebrew, no Mac password, no developer-tools window: everything goes in your home folder.
  if [ -n "${TADCLIP_SRC:-}" ]; then   # rehearsals: a local copy instead of GitHub
    mkdir -p "$D" && (cd "$TADCLIP_SRC" && tar -c --exclude .git --exclude node_modules .) | tar -x -C "$D"
    echo "TadClip from $TADCLIP_SRC"
  # git only when Apple's developer tools are already there (without them /usr/bin/git just opens their install window)
  elif [ -d "$D/.git" ] && xcode-select -p >/dev/null 2>&1; then
    git -C "$D" pull -q --ff-only && echo "TadClip updated: $(git -C "$D" log -1 --format=%h)"
  else
    # skip the ~60 MB download when the code hasn't changed since the last run
    sha=$(curl -fsSL -m 20 "https://api.github.com/repos/$REPO/commits/main" 2>/dev/null | sed -n 's/^  "sha": "\([0-9a-f]*\)".*/\1/p' | head -1)
    if [ -n "$sha" ] && [ "$sha" = "$(cat "$D/.tadclip-commit" 2>/dev/null)" ]; then
      echo "TadClip is already the latest version (${sha:0:7})."
    else
      echo "Downloading TadClip ${sha:0:7} (~60 MB) · กำลังดาวน์โหลด TadClip"
      # ponytail: files deleted upstream stay behind on an update; harmless, re-install fresh if one ever matters
      mkdir -p "$D"
      curl -fsSL --retry 5 --retry-all-errors --connect-timeout 20 --speed-limit 1024 --speed-time 60 "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" | tar -xz --strip-components 1 -C "$D" || { echo "Download failed: check the internet and paste the line again · ดาวน์โหลดไม่สำเร็จ ตรวจอินเทอร์เน็ตแล้ววางคำสั่งเดิมอีกครั้ง"; return 1; }
      [ -n "$sha" ] && echo "$sha" > "$D/.tadclip-commit"
    fi
  fi

  echo "Installing. About 10 minutes, up to 30 on a slow connection · กำลังติดตั้ง ประมาณ 10 นาที เน็ตช้าอาจถึง 30 นาที"
  bash "$D/scripts/setup.sh" </dev/null; rc=$?
  echo "took $(( ($(date +%s) - t0) / 60 )) min"
  if [ $rc = 0 ]; then
    echo; cat "$D/docs/WELCOME.th.txt"; echo
    echo "Done. The TadClip page opens in your browser. Later: double-click TadClip on the Desktop, then TadClip.app."
    echo "เสร็จแล้ว หน้า TadClip จะเปิดขึ้นในเบราว์เซอร์ ครั้งต่อไป: ดับเบิลคลิก TadClip บนเดสก์ท็อป แล้วเปิด TadClip.app"
  else
    echo
    echo "Not finished yet (see the MISS lines above). Paste the same line again: it skips what's done."
    echo "ยังติดตั้งไม่ครบ ดูบรรทัด MISS ด้านบน แล้ววางคำสั่งเดิมอีกครั้ง ส่วนที่เสร็จแล้วจะข้ามไปเอง"
  fi
  return $rc
}
run() {
  L="$HOME/Library/Logs/TadClip"; mkdir -p "$L"; LOG="$L/install-$(date +%Y%m%d-%H%M%S).log"
  main "$@" 2>&1 | while IFS= read -r l; do printf '%s %s\n' "$(date +%H:%M:%S)" "$l"; done | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "Log: $LOG"
  exit "$rc"
}
run "$@" </dev/null
