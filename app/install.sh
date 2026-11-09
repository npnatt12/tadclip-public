#!/usr/bin/env bash
# Puts the TadClip app on this Mac: the ~/TadClip folder, a TadClip.app with the logo inside it, and a login item that
# starts the page at every login. setup.sh runs this; safe to re-run. No password: everything is in your home folder.
#   bash app/install.sh            install / update
#   bash app/install.sh --remove   take the login item and the .app away (your clips stay)
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${TADCLIP_DIR:-$HOME/TadClip}"; LA="$HOME/Library/LaunchAgents/com.tadclip.app.plist"; ID="gui/$(id -u)/com.tadclip.app"
if [ "${1:-}" = --remove ]; then launchctl bootout "$ID" 2>/dev/null; rm -rf "$LA" "$DIR/TadClip.app"; [ -L "$HOME/Desktop/TadClip" ] && rm "$HOME/Desktop/TadClip"; echo "TadClip app removed (clips kept in $DIR)"; exit 0; fi

NODE=""
for n in "$HOME/.local/bin/node" /opt/homebrew/opt/node@22/bin/node "$(command -v node 2>/dev/null)"; do
  [ -x "$n" ] && "$n" -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' 2>/dev/null && { NODE="$n"; break; }
done
[ -n "$NODE" ] || { echo "TadClip app: Node 22 not found (run scripts/setup.sh first)"; exit 1; }
# launchd can't run anything under ~/Desktop, ~/Documents or ~/Downloads (macOS privacy): the skill must live in ~/.claude
case "$S" in "$HOME/Desktop"*|"$HOME/Documents"*|"$HOME/Downloads"*) echo "TadClip app: $S is in a folder macOS won't let a login item read; install TadClip in ~/.claude/skills/tadclip"; exit 1;; esac
mkdir -p "$DIR/.tadclip" "$(dirname "$LA")"

# login item: the page server; restarts if it crashes, opens the page once at login
cat > "$LA" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.tadclip.app</string>
  <key>ProgramArguments</key><array><string>$NODE</string><string>$S/app/server.mjs</string><string>--open</string></array>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>$HOME/.local/bin:/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string><key>TADCLIP_DIR</key><string>$DIR</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>StandardOutPath</key><string>$DIR/.tadclip/server.log</string><key>StandardErrorPath</key><string>$DIR/.tadclip/server.log</string>
</dict></plist>
EOF
launchctl bootout "$ID" 2>/dev/null
[ "${TADCLIP_NO_START:-}" ] || launchctl bootstrap "gui/$(id -u)" "$LA"

# TadClip.app in the folder: starts the server if it isn't running, then opens the page
rm -rf "$DIR/TadClip.app"
osacompile -o "$DIR/TadClip.app" -e "do shell script \"curl -fs -m 2 http://127.0.0.1:4747/api/state >/dev/null || (launchctl kickstart $ID >/dev/null 2>&1 || ('$NODE' '$S/app/server.mjs' >/dev/null 2>&1 &)); sleep 1; open http://127.0.0.1:4747/\""
# the plain logo as the app's and the folder's icon (Finder shows it; nothing else changes)
for f in "$DIR/TadClip.app" "$DIR"; do
  osascript -l JavaScript -e "ObjC.import('AppKit'); \$.NSWorkspace.sharedWorkspace.setIconForFileOptions(\$.NSImage.alloc.initWithContentsOfFile('$S/app/icon/icon-1024.png'), '$f', 0)" >/dev/null 2>&1
done
# a shortcut to the folder on the Desktop (a first-timer finds the Desktop, not their home folder). A symlink, not a Finder
# alias: making an alias asks "allow to control Finder?". Never touches an existing Desktop/TadClip (names ignore case on a
# Mac: the 11-08 tester kept clips in Desktop/Tadclip). TADCLIP_NO_DESKTOP=1 skips it
[ -n "${TADCLIP_NO_DESKTOP:-}" ] || [ -e "$HOME/Desktop/TadClip" ] || [ -L "$HOME/Desktop/TadClip" ] || ln -s "$DIR" "$HOME/Desktop/TadClip"
echo "TadClip app: $DIR/TadClip.app (opens at login too; TadClip on the Desktop opens the folder)"
