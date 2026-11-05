#!/usr/bin/env bash
# TadClip in one line:
#   curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
# Safe to re-run: it updates what's already there.
set -eu
# all in main, so a half-downloaded script never runs
main() {
  REPO=${TADCLIP_REPO:-https://github.com/npnatt12/tadclip-public.git}
  D="$HOME/.claude/skills/tadclip"

  [ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] || echo "Note: TadClip is built for Apple silicon Macs. It may not work here."

  # git comes with Apple's command line tools
  if ! xcode-select -p >/dev/null 2>&1; then
    xcode-select --install 2>/dev/null || true
    echo "Click Install in the window that opened. When it finishes, run this line again."
    echo "กด Install ในหน้าต่างที่เปิดขึ้นมา รอจนเสร็จ แล้ววางบรรทัดเดิมอีกครั้ง"
    exit 1
  fi

  # Homebrew: its installer asks for your Mac password
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  if ! command -v brew >/dev/null; then
    echo "Installing Homebrew. Type your Mac password if it asks (nothing shows while you type)."
    echo "กำลังลง Homebrew ถ้าถามรหัสผ่าน ให้พิมพ์รหัสเครื่อง Mac ตอนพิมพ์จะไม่เห็นตัวอักษร เป็นเรื่องปกติ"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/tty
    eval "$(/opt/homebrew/bin/brew shellenv)"
    grep -qs 'brew shellenv' "$HOME/.zprofile" || echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
  fi

  if [ -d "$D/.git" ]; then
    git -C "$D" pull -q --ff-only
  else
    mkdir -p "$(dirname "$D")"
    git clone -q --depth 1 "$REPO" "$D"
  fi

  echo "Installing. This takes a few minutes · กำลังติดตั้ง รอสักครู่"
  bash "$D/scripts/setup.sh" </dev/null || true    # setup ends on "2 missing" until the keys are in

  if ! grep -qs '^GEMINI_API_KEY=.' "$D/.env" || ! grep -qs '^PEXELS_API_KEY=.' "$D/.env"; then
    [ -n "${TADCLIP_NO_OPEN:-}" ] || open -e "$D/.env"
    cat <<'NEXT'

Almost done. Your key file just opened. Paste a free key after each = sign, then save (⌘S):
ใกล้เสร็จแล้ว ไฟล์คีย์เปิดขึ้นมาแล้ว ขอคีย์ฟรีจากสองลิงก์นี้ วางต่อท้ายเครื่องหมาย = แล้วกด ⌘S เพื่อเซฟ

  GEMINI_API_KEY  https://aistudio.google.com/apikey
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
