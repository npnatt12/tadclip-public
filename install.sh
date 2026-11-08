#!/usr/bin/env bash
# TadClip in one line:
#   curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
# Safe to re-run: it updates what's already there.
set -eu
# all in main, so a half-downloaded script never runs
main() {
  REPO=${TADCLIP_REPO:-npnatt12/tadclip-public}
  D="$HOME/.claude/skills/tadclip"

  [ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] || echo "Note: TadClip is built for Apple silicon Macs. It may not work here."

  # No Homebrew, no Mac password, no developer-tools window: everything goes in your home folder.
  # git only when Apple's developer tools are already there (without them /usr/bin/git just opens their install window)
  if [ -d "$D/.git" ] && xcode-select -p >/dev/null 2>&1; then
    git -C "$D" pull -q --ff-only
  else
    # skip the ~60 MB download when the code hasn't changed since the last run
    sha=$(curl -fsSL -m 20 "https://api.github.com/repos/$REPO/commits/main" 2>/dev/null | sed -n 's/^  "sha": "\([0-9a-f]*\)".*/\1/p' | head -1)
    if [ -n "$sha" ] && [ "$sha" = "$(cat "$D/.tadclip-commit" 2>/dev/null)" ]; then
      echo "TadClip is already the latest version."
    else
      echo "Downloading TadClip (~60 MB) · กำลังดาวน์โหลด TadClip"
      # ponytail: files deleted upstream stay behind on an update; harmless, re-install fresh if one ever matters
      mkdir -p "$D"
      curl -fsSL --retry 5 --retry-all-errors "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" | tar -xz --strip-components 1 -C "$D"
      [ -n "$sha" ] && echo "$sha" > "$D/.tadclip-commit"
    fi
  fi

  echo "Installing. About 30-40 minutes · กำลังติดตั้ง ประมาณ 30-40 นาที"
  if bash "$D/scripts/setup.sh" </dev/null; then
    echo
    cat "$D/docs/WELCOME.th.txt"
    echo
    echo "Done. Quit and reopen the Claude app once, then start a new chat and say: ตัดต่อคลิปนี้ ~/Downloads/my-video.mov"
  else
    echo
    echo "Not finished yet (see the MISS lines above). Run the same install again: it skips what's done."
    echo "ยังติดตั้งไม่ครบ ดูบรรทัด MISS ด้านบน แล้ววางคำสั่งติดตั้งเดิมอีกครั้ง ส่วนที่เสร็จแล้วจะข้ามไปเอง"
    exit 1
  fi
}
main "$@"
