# Chalkboard · เขียนชอล์ก

A green chalkboard: lines appear as if written in chalk, one idea per board; the speaker returns between boards.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Chalkboard"). The preset is `styles/chalkboard.json` (`"style": "chalkboard"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- A `scene` `sentence` on the board (#1F3A2C): the words ink in as they're spoken, Sriracha (handwriting).
- The key word as the `hero` in chalk yellow (#F2D16B).
- Sounds: marker-scribble / pencil-write under each line. Bed: classical-7 (soft piano).

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "sentence",
  "at": 0.8,
  "to": 6.4,
  "lines": [
   "อย่ารีบ",
   "build มันขึ้นมา"
  ],
  "hero": {
   "text": "ทีละนิด",
   "at": 4.8,
   "color": "#F2D16B"
  }
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
