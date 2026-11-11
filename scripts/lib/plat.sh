# What differs between a Mac and Windows (Git Bash) for setup.sh, doctor.sh and ready.sh. Source it: . scripts/lib/plat.sh
case "$(uname -s)" in MINGW* | MSYS* | CYGWIN*) TC_WIN=1 ;; *) TC_WIN= ;; esac
# a venv's python: bin/python on a Mac, Scripts/python.exe on Windows
vpy() { if [ -n "$TC_WIN" ]; then echo "$1/Scripts/python.exe"; else echo "$1/bin/python"; fi; }
# Thai speech-to-text: mlx-whisper on Apple silicon; faster-whisper on Windows (same large-v3-turbo weights, CTranslate2
# int8 on the CPU; IMG_2260: CER 1.4 % vs mlx 1.5 %, word starts within 100 ms for 98.9 % of words)
if [ -n "$TC_WIN" ]; then THAI_VENV="$HOME/.venvs/fw"; THAI_MOD=faster_whisper; THAI_REPO=mobiuslabsgmbh/faster-whisper-large-v3-turbo; THAI_REQ=fw.txt
else THAI_VENV="$HOME/.venvs/mlxw"; THAI_MOD=mlx_whisper; THAI_REPO=mlx-community/whisper-large-v3-turbo; THAI_REQ=mlxw.txt; fi
THAI_PY="$(vpy "$THAI_VENV")"
sha256ok() { # SHA256 FILE: the file's checksum is this (sha256sum on Windows/Linux, shasum on a Mac)
  if command -v sha256sum >/dev/null; then echo "$1  $2" | sha256sum -c --status; else echo "$1  $2" | shasum -a 256 -c -s; fi; }

# machine: can this computer run TadClip? Sets TC_OK (1 or empty), TC_DESC (one line), TC_RAM (GB), and when not:
# TC_WHY_EN / TC_WHY_TH. Mac: Apple chip + macOS 14 (mlx's wheel is macosx_14_0_arm64). Windows: x64 (CTranslate2 has no
# Windows-on-ARM build) and Windows 10 1809+ (Claude Code's own floor).
machine() {
  TC_OK=; TC_WHY_EN=; TC_WHY_TH=
  if [ -n "$TC_WIN" ]; then
    local cap build arch cpu ram
    IFS='|' read -r cap build arch cpu ram < <(powershell.exe -NoProfile -NonInteractive -Command '$o=Get-CimInstance Win32_OperatingSystem; $p=Get-CimInstance Win32_Processor | Select-Object -First 1; $s=Get-CimInstance Win32_ComputerSystem; "{0}|{1}|{2}|{3}|{4}" -f $o.Caption,$o.BuildNumber,$p.Architecture,$p.Name.Trim(),[math]::Round($s.TotalPhysicalMemory/1GB)' 2>/dev/null | tr -d '\r')
    TC_RAM=${ram:-0}; TC_DESC="${cpu:-?}, ${cap:-Windows} (build ${build:-?}), RAM ${TC_RAM} GB"
    if [ "${arch:-}" = 9 ] && [ "${build:-0}" -ge 17763 ] 2>/dev/null; then TC_OK=1
    else
      TC_WHY_EN="TadClip needs 64-bit Windows 10 (version 1809 or newer) or Windows 11 on an Intel or AMD processor. This one: $TC_DESC."
      TC_WHY_TH="เครื่องนี้ใช้ TadClip ไม่ได้: ต้องเป็น Windows 10 (1809 ขึ้นไป) หรือ Windows 11 แบบ 64 บิต ชิป Intel หรือ AMD เครื่องนี้: $TC_DESC"
    fi
  else
    local mac; mac=$(sw_vers -productVersion 2>/dev/null)
    TC_RAM=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1073741824 ))
    TC_DESC="$(sysctl -n machdep.cpu.brand_string 2>/dev/null | sed 's/Apple //'), macOS ${mac:-?}, RAM $TC_RAM GB"
    if [ "$(uname -sm)" = "Darwin arm64" ] && [ "${mac%%.*}" -ge 14 ] 2>/dev/null; then TC_OK=1
    else
      TC_WHY_EN="TadClip needs a Mac with an Apple chip (M1 or newer) and macOS 14 or newer. This one: $(uname -sm), macOS ${mac:-?}."
      TC_WHY_TH="เครื่องนี้ใช้ TadClip ไม่ได้: ต้องเป็น Mac ชิป Apple (M1 ขึ้นไป) และ macOS 14 ขึ้นไป เครื่องนี้: $(uname -m), macOS ${mac:-?}"
    fi
  fi
}
freegb() { df -k "$HOME" | awk 'NR==2{print int($4/1048576)}'; }
# run directly: `bash scripts/lib/plat.sh thai` prints this machine's Thai-engine python (recipes: TPY=$(bash $S/scripts/lib/plat.sh thai))
[ "${BASH_SOURCE[0]}" = "$0" ] && [ "${1:-}" = thai ] && echo "$THAI_PY"; :   # sourced: always status 0
