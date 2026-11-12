# Boxed UI · การ์ดกลางจอ

One white card in the middle of a light grey screen: a small setup line, then the key word in red.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Boxed UI"). The preset is `styles/boxed-ui.json` (`"style": "boxed-ui"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- `scene` `card` on #F2F2F2: a small grey setup line, then the `pill` (the red key word) with the cursor click.
- One card per point, 2–3 s. Sounds: click-1 on the pill. Bed: lo-fi-02.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "card",
  "at": 0.8,
  "to": 4.4,
  "lines": [
   {
    "text": "จีบกันมาสองเดือน แล้วค่อยไป",
    "at": 1.0,
    "size": 64,
    "color": "#777777"
   }
  ],
  "pill": {
   "text": "เดตแรก",
   "at": 2.0
  },
  "cursor": {
   "clickAt": 2.8
  }
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
