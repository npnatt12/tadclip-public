#!/usr/bin/env bash
# Gathers everything about this Mac's TadClip runs into one folder for a bug report or a test review:
# the install logs, the app's event log and run records, each reel's progress lines and render logs, recent TadClip
# chats, a doctor run and the versions. It goes to /Users/Shared so another account on this Mac can read it.
#   bash ~/.claude/skills/tadclip/scripts/logs.sh          (or tell Claude: "เก็บบันทึก TadClip")
# Holds the transcripts of your clips; keys in .env are never copied.
set -u
S="$(cd "$(dirname "$0")/.." && pwd)"; DIR="${TADCLIP_DIR:-$HOME/TadClip}"
OUT="${TADCLIP_LOGS_OUT:-/Users/Shared/TadClip-logs}/$(whoami)-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"/{install,app,reels,chats}
cp "$HOME"/Library/Logs/TadClip/*.log "$OUT/install/" 2>/dev/null
cp "$DIR"/.tadclip/{events.log,server.log,job.json,settings.json} "$OUT/app/" 2>/dev/null
cp "$DIR"/.tadclip/*.stream.jsonl "$OUT/app/" 2>/dev/null
for p in "$DIR"/*/build/progress.log; do [ -f "$p" ] || continue; n=$(basename "$(dirname "$(dirname "$p")")")
  mkdir -p "$OUT/reels/$n"; cp "$p" "$OUT/reels/$n/"; cp "$DIR/$n"/finals/*.log "$DIR/$n"/finals/*.qa.json "$OUT/reels/$n/" 2>/dev/null; done
# their brand folder (names and sizes only: their logo stays theirs) and what the brand kit made of it per reel
mkdir -p "$OUT/brand"; ls -la "$DIR/brand" > "$OUT/brand/folder.txt" 2>&1; ls -la "$DIR/brands" "$DIR"/brands/* >> "$OUT/brand/folder.txt" 2>/dev/null
python3 "$(dirname "$0")/own_brand.py" --show --from "$DIR/brand" > "$OUT/brand/show.json" 2> "$OUT/brand/show.err"   # what the page saw
for k in "$DIR"/*/brand/own.json; do [ -f "$k" ] && cp "$k" "$OUT/brand/$(basename "$(dirname "$(dirname "$k")")")-own.json"; done
# the chats of the last 3 days that ran TadClip (the prompts typed in Claude, and what it did)
find "$HOME/.claude/projects" -name "*.jsonl" -mtime -3 2>/dev/null | while read -r f; do
  grep -q -i "tadclip" "$f" && cp "$f" "$OUT/chats/$(basename "$(dirname "$f")")--$(basename "$f")"; done
{ echo "collected $(date '+%Y-%m-%d %H:%M:%S %z') by $(whoami)"
  sw_vers 2>/dev/null; uname -m; df -h "$HOME" | tail -1
  echo "tadclip $(git -C "$S" log -1 --format='%h %cd' 2>/dev/null || cat "$S/.tadclip-commit" 2>/dev/null)"
  export PATH="$HOME/.local/bin:/opt/homebrew/opt/node@22/bin:$PATH"
  for c in claude codex node ffmpeg uv; do v=$($c --version 2>/dev/null || $c -version 2>/dev/null); printf '%-7s %s\n' "$c" "${v%%$'\n'*}"; done
  launchctl print "gui/$(id -u)/com.tadclip.app" 2>/dev/null | grep -E "state =|last exit" | head -2
} > "$OUT/versions.txt" 2>&1
bash "$S/scripts/doctor.sh" > "$OUT/doctor.txt" 2>&1
# keys never leave: every value in .env, and anything shaped like a Google / Anthropic / OpenAI key, is blanked out in
# every collected file (a key pasted into a chat once would otherwise sit in a folder every account on this Mac can read)
export TADCLIP_SECRETS="$(sed -n 's/^[A-Z_]*=\(..*\)$/\1/p' "$S/.env" 2>/dev/null | tr '\n' '\t')"
find "$OUT" -type f -exec perl -pi -e 'BEGIN { @k = grep { length > 7 } split /\t/, $ENV{TADCLIP_SECRETS} }
  for my $k (@k) { s/\Q$k\E/[key removed]/g } s/\b(AIza[0-9A-Za-z_-]{30,}|AQ\.[0-9A-Za-z_-]{30,}|sk-(ant-)?[0-9A-Za-z_-]{20,})/[key removed]/g' {} +
chmod -R a+rX "$OUT"
echo "TadClip logs: $OUT ($(du -sh "$OUT" | cut -f1))"
echo "เก็บบันทึกไว้ที่: $OUT"
