# Board + face · หน้าบน กระดานล่าง

A whiteboard drawing in a framed panel while the speaker stays on screen: the board explains, the face keeps trust.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Board + face"). The preset is `styles/board-face.json` (`"style": "board-face"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- `broll` with `mode: "panel"`: a board image or a drawn clip (recipes/whiteboard makes them) in a framed box; the speaker stays.
- A handwritten `impact` (Sriracha via `font`) for the word on the board.
- Sounds: marker-scribble while it draws. Bed: forest-mist-whispers.

## Example beats

```json
[
 {
  "type": "broll",
  "src": "assets/broll/board.mp4",
  "at": 0.8,
  "to": 5.6,
  "mode": "panel"
 },
 {
  "type": "impact",
  "at": 6.2,
  "to": 8.4,
  "text": "คนที่รู้วิธี",
  "role": "note"
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
