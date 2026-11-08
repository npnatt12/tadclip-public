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
    # ponytail: files deleted upstream stay behind on an update; harmless, re-install fresh if one ever matters
    mkdir -p "$D"
    curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" | tar -xz --strip-components 1 -C "$D"
  fi

  echo "Installing. This takes a few minutes · กำลังติดตั้ง รอสักครู่"
  bash "$D/scripts/setup.sh" </dev/null || true    # setup ends on "1 missing" until the Gemini key is in

  if ! grep -qs '^GEMINI_API_KEY=.' "$D/.env"; then
    [ -n "${TADCLIP_NO_OPEN:-}" ] || open -e "$D/.env"
    cat <<'NEXT'

Almost done. Your key file just opened. Paste a free Gemini key after GEMINI_API_KEY=, then save (⌘S):
ใกล้เสร็จแล้ว ไฟล์คีย์เปิดขึ้นมาแล้ว ขอคีย์ Gemini ฟรีจากลิงก์นี้ วางต่อจาก GEMINI_API_KEY= แล้วกด ⌘S เพื่อเซฟ

  GEMINI_API_KEY  https://aistudio.google.com/apikey

Optional, for more stock footage · ไม่บังคับ ถ้าอยากได้ฟุตเทจสต็อกเพิ่ม:
  PEXELS_API_KEY  https://www.pexels.com/api/key/

NEXT
  fi
  cat <<'NEXT'
Then start a new Claude Code or Codex session and say:
จากนั้นเปิดเซสชันใหม่ใน Claude Code หรือ Codex แล้วสั่งแบบนี้:

  ตัดต่อคลิปนี้ ~/Downloads/my-video.mov

NEXT
}
main "$@"
