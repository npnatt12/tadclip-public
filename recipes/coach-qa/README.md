# Coach Q&A

A seated coach answers one question (Thai first). The question card is the hook, the face stays clean (no running
captions), each point is a stock B-roll insert with a two-tier label behind a grainy colour swipe, a tilted keyword now
and then, a LINE CTA for the back third, a silent white logo end card. Modelled on @clubgig_official's grammar.

Read SYSTEM.md first; house.json is the fixed look, catalog.json what each reel used.

## Calls
- "Coach Q&A", "coach style", "like clubgig", "relationship coach reel"

## What it needs
The raw cut (assets/talk.mp4 muted plate + assets/voice.wav, pauses already trimmed), build/words.cut.json for the
onsets, 2-3 stock B-roll clips (stock allowed in this style). Anuphan (OFL) and SFX are copied by the builder.

## Build
```bash
S=~/.claude/skills/tadclip
python3 $S/recipes/coach-qa/coachqa.py           # prints the usage block
python3 $P/tools/build.py                         # index.html, build/beats.json, build/coverage.txt
bash $S/scripts/hf.sh lint $P                     # 0 errors (nested-structure warnings are expected)
bash $S/scripts/hf.sh snapshot $P --at <beat times> --no-end --describe false
python3 $S/scripts/finals.py preview $P --out $P/finals --style "Coach Q&A" --code R01 --title "..."   # WAIT for the OK
```

Builder: `coachqa.py`, class `Coach`: `snaps()`, `bug()`, `qcard()`, `broll()` (+ label, swipes in/out), `swipe()`,
`keyword()`, `cta()`, `endcard()`, `sfx()`, `build()`.
