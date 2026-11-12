# Split demo · จอบน หน้าล่าง

A demo: the screen (or the thing being shown) fills the top half, the speaker the bottom half, a label between.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Split demo"). The preset is `styles/split-demo.json` (`"style": "split-demo"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- `broll` beats with `mode: "split"` (`h` ~900, `shift` to keep the face), each held for the whole step it shows.
- A label on each (`label: [big, small]`) naming the step.
- Screen recordings: phone or laptop captures from the user, or `scene` `ui` for a typed prompt.
- Sounds: click-1 / tick on actions. Bed: infinity.

## Example beats

```json
[
 {
  "type": "broll",
  "src": "assets/broll/m1.mp4",
  "at": 0.6,
  "to": 5.4,
  "mode": "split",
  "h": 900,
  "shift": 380,
  "label": [
   "ขั้นที่ 1",
   "ทักมาได้เลยครับ"
  ]
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
