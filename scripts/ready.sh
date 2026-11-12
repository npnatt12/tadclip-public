#!/usr/bin/env bash
# Before a class: is this computer ready to cut a reel? Checks the Mac or PC, the install, Claude (signed in, a paid plan) and makes
# a real 2-second Thai render through the same renderer a reel uses. Ends with one line to paste in the class's LINE
# group: "TADCLIP READY ..." with a short code, or "TADCLIP NOT READY" and, above it, what to fix in Thai.
#   bash ~/.claude/skills/tadclip/scripts/ready.sh        (or tell Claude: "เช็กความพร้อม TadClip")
# Windows, in PowerShell (UTF-8 for the Thai; Git Bash is where install.ps1 recorded it; CI runs this line from the sheet):
#   [Console]::OutputEncoding=[Text.Encoding]::UTF8; & $env:CLAUDE_CODE_GIT_BASH_PATH "$HOME/.claude/skills/tadclip/scripts/ready.sh"
# The code is a checksum of this Mac's line and the date: it tells the organiser the line came from a run today, not a
# copy of someone else's. It proves nothing more; the class still sees the reel.
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
. "$S/scripts/lib/plat.sh"   # machine (this computer: Mac or Windows), TC_WIN
export PATH="$HOME/.local/bin:$HOME/.local/share/tadclip-tools/node:/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:$PATH"
fix=(); good=()
no() { fix+=("$1"); echo "  ✗ $1"; }
yes() { good+=("$1"); echo "  ✓ $1"; }

echo "TadClip: เช็กความพร้อมก่อนเรียน · readiness check"
machine; ram=$TC_RAM; free=$(freegb)
if [ -n "$TC_OK" ]; then yes "$([ -n "$TC_WIN" ] && echo Windows || echo Mac): $TC_DESC"; else no "$TC_WHY_TH"; fi
# ponytail: 8 GB machines are untested (every test ran on 16 GB); a note, not a failure, until one is measured
[ "$ram" -lt 16 ] && echo "    หมายเหตุ: RAM $ram GB ยังไม่เคยทดสอบ อาจช้ากว่าปกติ"
# a reel's working files: ~1-2 GB per clip (project folder, renders)
[ "$free" -ge 5 ] && yes "พื้นที่ว่าง $free GB" || no "พื้นที่ว่างเหลือ $free GB: ลบไฟล์ที่ไม่ใช้ให้ว่างอย่างน้อย 5 GB"

# the install: doctor.sh's own verdict (its last line is "N ok, M missing")
d=$(bash "$S/scripts/doctor.sh" 2>&1 | tail -1); m=$(echo "$d" | sed -n 's/.*, \([0-9]*\) missing/\1/p')
[ "${m:-1}" = 0 ] && yes "ติดตั้งครบ ($d)" || no "ติดตั้งยังไม่ครบ ($d): วางบรรทัดติดตั้งอีกครั้ง หรือบอก Claude ว่า \"ติดตั้ง TadClip ต่อ\""

# Claude: the same places the TadClip app looks (CLI, else the desktop app's own copy)
bin=""; for c in "$HOME/.local/bin/claude" "$HOME/.local/bin/claude.exe" /opt/homebrew/bin/claude /usr/local/bin/claude \
  "$HOME"/Library/Application\ Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude; do [ -x "$c" ] && { bin=$c; break; }; done
plan="-"
if [ -z "$bin" ]; then no "ยังไม่มี Claude ในเครื่อง: $([ -n "$TC_WIN" ] && echo "วางบรรทัดติดตั้ง TadClip อีกครั้ง (ติดตั้ง Claude ให้เอง)" || echo "ติดตั้งแอป Claude จาก claude.ai/download")"
else
  a=$("$bin" auth status 2>/dev/null)
  plan=$(echo "$a" | python3 -c 'import json,sys
try: d=json.load(sys.stdin); print(d.get("subscriptionType") or d.get("planTier") or "-") if d.get("loggedIn") else print("out")
except Exception: print("?")' 2>/dev/null)
  case "$plan" in
    out|"?") no "Claude ยังไม่ได้เข้าสู่ระบบ: เปิดหน้า TadClip แล้วกด \"เข้าสู่ระบบ Claude\"";;
    free) no "บัญชี Claude เป็นแบบฟรี: TadClip ต้องใช้ Claude Pro หรือ Max (ตัวเลือกใน claude.ai > Settings > Billing)";;
    *) yes "Claude: เข้าสู่ระบบแล้ว (แผน $plan)";;
  esac
fi

# a real render: 2 s of Thai text, GSAP, the pinned HyperFrames, headless Chrome, ffmpeg (what every reel goes through)
R="$HOME/TadClip/.tadclip/ready"; rm -rf "$R"; mkdir -p "$R"; cp "$S/library/fonts/thai/kanit-thai.woff2" "$R/"
cat > "$R/index.html" <<'HTML'
<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>@font-face{font-family:Kanit;src:url(kanit-thai.woff2)} html,body{margin:0;background:#6A2C3B}
#t{position:absolute;top:820px;width:1080px;text-align:center;font:700 140px Kanit;color:#FFE11A}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="2" data-fps="30">
<div id="t">พร้อมแล้ว</div></div>
<script>window.__timelines = window.__timelines || {}; const tl = gsap.timeline({ paused: true });
tl.from("#t", { scale: 0.4, opacity: 0, duration: 1, ease: "back.out" }); window.__timelines["main"] = tl;</script></body></html>
HTML
t0=$(date +%s)
(cd "$R" && bash "$S/scripts/hf.sh" render -o ready.mp4) > "$R/render.log" 2>&1
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$R/ready.mp4" 2>/dev/null)
if awk -v d="${dur:-0}" 'BEGIN{exit !(d >= 1.8 && d <= 2.3)}'; then yes "ทดลองทำวิดีโอ 2 วินาที: สำเร็จ ($(( $(date +%s) - t0 )) วินาที)"
else no "ทดลองทำวิดีโอไม่สำเร็จ: บอก Claude ว่า \"เก็บบันทึก TadClip\" แล้วส่งโฟลเดอร์ให้ทีมในกลุ่ม LINE"; tail -3 "$R/render.log" | sed 's/^/    /'; fi

# the public edition's version (CHANGELOG.md), else the commit (a curl install stamps it, a git checkout has it)
ver=$(sed -n 's/^## \(v[0-9.]*\).*/\1/p' "$S/CHANGELOG.md" 2>/dev/null | head -1)
c=$(cat "$S/.tadclip-commit" 2>/dev/null | cut -c1-7); [ -n "$c" ] || c=$(git -C "$S" rev-parse --short HEAD 2>/dev/null)
ver="${ver:-}${ver:+${c:+ }}${c:-}"; [ -n "$ver" ] || ver="?"
line="$TC_DESC · ${free}GB free · Claude ${plan} · build $ver · $(date +%Y-%m-%d)"
echo
if [ ${#fix[@]} = 0 ]; then
  code=$(printf '%s' "$line" | { command -v sha256sum >/dev/null && sha256sum || shasum -a 256; } | cut -c1-6 | tr a-f A-F)
  out="TADCLIP READY ✓ $code · $line"
  echo "พร้อมเรียนแล้ว! คัดลอกบรรทัดล่างนี้ไปวางในกลุ่ม LINE ของคลาส:"
else
  out="TADCLIP NOT READY · ${#fix[@]} ข้อต้องแก้ · $line"
  echo "ยังไม่พร้อม: แก้ข้อที่มี ✗ ด้านบนแล้วเช็กอีกครั้ง ถ้าแก้ไม่ได้ ส่งบรรทัดล่างนี้ในกลุ่ม LINE ทีมจะช่วย:"
fi
echo "$out"; echo "$(date '+%F %T') $out" >> "$HOME/TadClip/.tadclip/ready.log"
[ ${#fix[@]} = 0 ]
