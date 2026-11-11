# TadClip on Windows in one line (PowerShell, or pasted into Claude Code):
#   irm https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.ps1 | iex
# A given version (to go back if a new one breaks): $env:TADCLIP_REF='v0.2.0'; irm ... | iex
# The Mac line is install.sh; run in Git Bash on Windows it hands over to this. No admin rights: everything goes in the
# user's own folders. Safe to re-run: it skips what's done. Every line is kept, with the time, in
# %LOCALAPPDATA%\TadClip\Logs\install-<date>.log (scripts/logs.sh collects it for a bug report).
# All in one function, called on the last line: a half-downloaded script never runs.
function Install-TadClip {
  $ErrorActionPreference = 'Continue'; $ProgressPreference = 'SilentlyContinue'   # the progress bar makes downloads ~10x slower in PowerShell 5
  [Console]::OutputEncoding = [Text.Encoding]::UTF8                              # Thai lines, ours and setup.sh's
  [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
  $Repo = if ($env:TADCLIP_REPO) { $env:TADCLIP_REPO } else { 'npnatt12/tadclip-public' }
  $Ref = if ($env:TADCLIP_REF) { $env:TADCLIP_REF } else { 'main' }
  $D = Join-Path $HOME '.claude\skills\tadclip'; $Tools = Join-Path $HOME '.local\share\tadclip-tools'
  $Logs = Join-Path $env:LOCALAPPDATA 'TadClip\Logs'; New-Item -ItemType Directory -Force -Path $Logs, $Tools | Out-Null
  $Log = Join-Path $Logs ("install-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date)); $t0 = Get-Date
  # SHA-256 with .NET itself: Get-FileHash lives in a module that may not load, and inside an if() a missing command
  # skips the whole check (CI 11-11 saw exactly that): this fails closed
  function Sha256([string]$f) { $s = [IO.File]::OpenRead($f); try { -join ([Security.Cryptography.SHA256]::Create().ComputeHash($s) | ForEach-Object { $_.ToString('X2') }) } finally { $s.Dispose() } }
  function Say([string]$m) { $l = "{0:HH:mm:ss} {1}" -f (Get-Date), $m; Write-Host $l; Add-Content -LiteralPath $Log -Value $l -Encoding UTF8 }

  Say 'TadClip install · ติดตั้ง TadClip'
  # the same stop as setup.sh (scripts/lib/plat.sh), before any download: x64 (the Thai speech engine has no Windows-on-ARM
  # build), Windows 10 1809+ (Claude Code's floor), ~8 GB free on a first install
  $os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
  $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
  $free = [math]::Floor((Get-PSDrive ($HOME.Substring(0, 1))).Free / 1GB)
  Say ("windows: {0} build {1} · {2} · RAM {3} GB · free disk: {4} GB · user: {5}" -f $os.Caption, $os.BuildNumber, $cpu.Name.Trim(), $ram, $free, $env:USERNAME)
  if ($cpu.Architecture -ne 9 -or [int]$os.BuildNumber -lt 17763) {
    Say 'TADCLIP_STATUS=unsupported: TadClip needs 64-bit Windows 10 (version 1809 or newer) or Windows 11 on an Intel or AMD processor.'
    Say 'เครื่องนี้ใช้ TadClip ไม่ได้: ต้องเป็น Windows 10 (1809 ขึ้นไป) หรือ Windows 11 แบบ 64 บิต ชิป Intel หรือ AMD'; return 2
  }
  if (-not (Test-Path -LiteralPath $D) -and $free -lt 8) {
    Say "TADCLIP_STATUS=no_space: TadClip needs about 8 GB free; this computer has $free GB. Free some space, then paste the line again."
    Say "พื้นที่ไม่พอ: ต้องว่างประมาณ 8 GB ตอนนี้ว่าง $free GB ลบไฟล์ที่ไม่ใช้ออกก่อน แล้ววางคำสั่งเดิมอีกครั้ง"; return 2
  }
  if ($ram -lt 8) { Say "หมายเหตุ: RAM $ram GB น้อยกว่าที่ทดสอบไว้ (8 GB ขึ้นไป) อาจช้ามาก · Note: $ram GB RAM is below the tested 8 GB" }

  # Git Bash: TadClip's scripts are bash, and Claude Code runs its Bash tool through it. An existing Git for Windows, else
  # a portable copy in our tools folder (no installer, no admin), pinned and checked like every other download
  $bash = @("$env:ProgramFiles\Git\bin\bash.exe", "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe", "$Tools\git\bin\bash.exe") | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
  if (-not $bash) {
    Say 'Git for Windows (portable, ~60 MB) · กำลังติดตั้ง Git'
    $url = 'https://github.com/git-for-windows/git/releases/download/v2.56.1.windows.1/PortableGit-2.56.1-64-bit.7z.exe'
    $sfx = Join-Path $Tools 'PortableGit.7z.exe'
    try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $sfx } catch { Say "Download failed: $url ($($_.Exception.Message)) · ดาวน์โหลดไม่สำเร็จ ตรวจอินเทอร์เน็ตแล้ววางคำสั่งเดิมอีกครั้ง"; return 1 }
    $h = try { Sha256 $sfx } catch { '' }
    if ($h -ne '9DD04A608CEB5F6AB32A73709E0ECB159D211DA71B697C45FF81F6DD0C6B49C7') { Remove-Item -LiteralPath $sfx; Say "download changed or unreadable: PortableGit (checksum $h)"; return 1 }
    $p = Start-Process -FilePath $sfx -ArgumentList '-y', "-o`"$Tools\git`"" -Wait -PassThru -WindowStyle Hidden
    Remove-Item -LiteralPath $sfx -ErrorAction SilentlyContinue
    $bash = "$Tools\git\bin\bash.exe"
    if (-not (Test-Path -LiteralPath $bash)) { Say "Git did not unpack (exit $($p.ExitCode))"; return 1 }
  }
  # Claude Code finds Git Bash here (its docs: CLAUDE_CODE_GIT_BASH_PATH); git.exe on PATH for TadClip's own updates
  [Environment]::SetEnvironmentVariable('CLAUDE_CODE_GIT_BASH_PATH', $bash, 'User'); $env:CLAUDE_CODE_GIT_BASH_PATH = $bash
  $gitDir = Split-Path -Parent (Split-Path -Parent $bash); $env:Path = "$gitDir\cmd;$env:Path"
  Say "git bash: $bash"

  # Claude Code, with Anthropic's own installer (claude.exe in %USERPROFILE%\.local\bin); the TadClip page signs in later
  $claude = Join-Path $HOME '.local\bin\claude.exe'
  if (-not (Test-Path -LiteralPath $claude) -and -not $env:TADCLIP_NO_CLAUDE) {
    Say 'Claude Code (Anthropic installer) · กำลังติดตั้ง Claude Code'
    # in its own scope (& { }): that script sets $ErrorActionPreference = 'Stop', and leaked into ours it turned setup.sh's
    # first stderr line into a fatal error that ended the install (CI 11-11 run 5)
    # its output to the screen (Out-Host), not into our return value
    try { & { Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression } | Out-Host } catch { Say "Claude Code install failed: $($_.Exception.Message)" }
    $ErrorActionPreference = 'Continue'
  }
  Say ("agents: claude {0} · codex {1}" -f $(if (Test-Path -LiteralPath $claude) { (& $claude --version 2>$null | Select-Object -First 1) } else { 'none' }), $(if (Get-Command codex -ErrorAction SilentlyContinue) { 'yes' } else { 'none' }))

  # TadClip itself: a git checkout (updates are a pull), or a local copy for rehearsals (TADCLIP_SRC)
  if ($env:TADCLIP_SRC) {
    New-Item -ItemType Directory -Force -Path $D | Out-Null
    & robocopy $env:TADCLIP_SRC $D /E /XD .git node_modules /NFL /NDL /NJH /NJS /NP | Out-Null
    Say "TadClip from $env:TADCLIP_SRC"
  } elseif (Test-Path -LiteralPath (Join-Path $D '.git')) {
    & git -C $D fetch -q --depth 1 origin $Ref 2>&1 | Out-Null; & git -C $D checkout -q -f FETCH_HEAD 2>&1 | Out-Null
    Say "TadClip updated: $(& git -C $D log -1 --format=%h)"
  } else {
    Say "Downloading TadClip $Ref (~60 MB) · กำลังดาวน์โหลด TadClip"
    if (Test-Path -LiteralPath $D) { Remove-Item -Recurse -Force -LiteralPath $D }
    & git -c core.longpaths=true clone -q --depth 1 --branch $Ref "https://github.com/$Repo.git" $D 2>&1 | ForEach-Object { Say "$_" }
    if (-not (Test-Path -LiteralPath (Join-Path $D 'scripts\setup.sh'))) { Say 'Download failed: check the internet and paste the line again · ดาวน์โหลดไม่สำเร็จ ตรวจอินเทอร์เน็ตแล้ววางคำสั่งเดิมอีกครั้ง'; return 1 }
    & git -C $D config core.longpaths true
  }

  Say 'Installing. About 15 minutes, up to 40 on a slow connection · กำลังติดตั้ง ประมาณ 15 นาที เน็ตช้าอาจถึง 40 นาที'
  $setup = (Join-Path $D 'scripts\setup.sh') -replace '\\', '/'
  $env:HOME = $HOME   # Git Bash's home = this user's profile (a HOME left over from another tool would send downloads elsewhere)
  & $bash --noprofile --norc $setup 2>&1 | ForEach-Object { Say "$_" }; $rc = $LASTEXITCODE
  Say ("took {0} min" -f [math]::Round(((Get-Date) - $t0).TotalMinutes))
  if ($rc -eq 0) {
    Get-Content -LiteralPath (Join-Path $D 'docs\WELCOME.th.txt') -Encoding UTF8 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
    Say 'Done. The TadClip page opens in your browser. Later: double-click TadClip on the Desktop.'
    Say 'เสร็จแล้ว หน้า TadClip จะเปิดขึ้นในเบราว์เซอร์ ครั้งต่อไป: ดับเบิลคลิก TadClip บนเดสก์ท็อป'
  } else {
    Say 'Not finished yet (see the MISS lines above). Paste the same line again: it skips what''s done.'
    Say 'ยังติดตั้งไม่ครบ ดูบรรทัด MISS ด้านบน แล้ววางคำสั่งเดิมอีกครั้ง ส่วนที่เสร็จแล้วจะข้ามไปเอง'
  }
  Write-Host "Log: $Log"
  return $rc
}
$global:LASTEXITCODE = Install-TadClip
