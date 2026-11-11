# The TadClip app on Windows (what app/install.sh does on a Mac): the TadClip folder, a "TadClip" shortcut on the Desktop
# and in the Start menu that starts the page and opens it, and one in Startup so it starts at every login. setup.sh runs
# this; safe to re-run. No admin: everything is in the user's own folders.
#   powershell -NoProfile -ExecutionPolicy Bypass -File app\install.ps1 [-NoStart] [-Remove]
param([switch]$NoStart, [switch]$Remove)
$ErrorActionPreference = 'Stop'
$S = Split-Path -Parent $PSScriptRoot
$Dir = if ($env:TADCLIP_DIR) { $env:TADCLIP_DIR } else { Join-Path $HOME 'TadClip' }
# the real Desktop: OneDrive often moves it (C:\Users\<name>\OneDrive\Desktop), and in Thai Windows its name is localised
# ('Create': in a new profile a folder that doesn't exist yet comes back as an empty path)
$Desk = [Environment]::GetFolderPath('Desktop', 'Create'); $Menu = [Environment]::GetFolderPath('Programs', 'Create'); $Boot = [Environment]::GetFolderPath('Startup', 'Create')
$Links = @{ (Join-Path $Desk 'TadClip.lnk') = $false; (Join-Path $Menu 'TadClip.lnk') = $false; (Join-Path $Boot 'TadClip.lnk') = $true }
if ($Remove) { $Links.Keys | ForEach-Object { Remove-Item -LiteralPath $_ -ErrorAction SilentlyContinue }; "TadClip app removed (clips kept in $Dir)"; exit 0 }

$Node = Join-Path $HOME '.local\share\tadclip-tools\node\node.exe'
if (-not (Test-Path -LiteralPath $Node)) { $Node = (Get-Command node -ErrorAction SilentlyContinue).Source }
if (-not $Node) { 'TadClip app: Node 22 not found (run scripts/setup.sh first)'; exit 1 }
$State = Join-Path $Dir '.tadclip'; New-Item -ItemType Directory -Force -Path $State | Out-Null

# start.ps1: the page server, hidden, kept alive (restarted after a crash, as the Mac's login item does); if it already
# answers, just open the page. -Login: the Startup copy (opens the page too, like the Mac at login)
$Start = Join-Path $State 'start.ps1'
@"
`$ErrorActionPreference = 'SilentlyContinue'
`$url = 'http://127.0.0.1:4747/'
try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 (`$url + 'api/state') | Out-Null; Start-Process `$url; exit 0 } catch {}
`$opened = `$false
while (`$true) {
  `$p = Start-Process -PassThru -WindowStyle Hidden -FilePath '$Node' -ArgumentList '"$S\app\server.mjs"' -WorkingDirectory '$Dir' -RedirectStandardOutput '$State\server.log' -RedirectStandardError '$State\server.err.log'
  if (-not `$opened) { Start-Sleep 2; Start-Process `$url; `$opened = `$true }
  `$p.WaitForExit()
  if (`$p.ExitCode -eq 0) { break }   # 0: stopped on purpose, or another copy already runs
  Start-Sleep 5
}
"@ | Set-Content -LiteralPath $Start -Encoding UTF8

# the logo as the shortcut's icon (Windows wants .ico)
$Ico = Join-Path $S 'app\icon\icon.ico'
if (-not (Test-Path -LiteralPath $Ico)) { & ffmpeg -v error -y -i (Join-Path $S 'app\icon\icon-1024.png') -vf scale=256:256 $Ico 2>$null }
$sh = New-Object -ComObject WScript.Shell
# WScript can't save into a folder with Thai letters in its path (CI 11-11, account สมศรี): each is saved in an ASCII
# folder under ProgramData, then moved into place
$tmp = Join-Path $env:ProgramData ('tadclip-lnk-' + [guid]::NewGuid().ToString('N')); New-Item -ItemType Directory $tmp | Out-Null
try {
  foreach ($l in $Links.Keys) {
    $t = Join-Path $tmp 'TadClip.lnk'; $k = $sh.CreateShortcut($t)
    $k.TargetPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $k.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Start`""
    $k.WorkingDirectory = $Dir; $k.WindowStyle = 7; $k.Description = 'TadClip: ตัดต่อคลิป'
    if (Test-Path -LiteralPath $Ico) { $k.IconLocation = "$Ico,0" }
    $k.Save(); Move-Item -Force -LiteralPath $t -Destination $l
  }
} finally { Remove-Item -Recurse -Force -LiteralPath $tmp -ErrorAction SilentlyContinue }
if (-not $NoStart) { Start-Process -WindowStyle Hidden -FilePath (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe') -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Start`"" }
"TadClip app: shortcuts on the Desktop ($Desk), in the Start menu and in Startup; clips go in $Dir"
