# Paper collage · คอลลาจกระดาษ

Cut-paper collage on a warm paper board: tilted photo cut-outs with tape, headline strips in a slab serif, grain.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Paper collage"). The preset is `styles/paper-collage.json` (`"style": "paper-collage"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- One `polaroid` per idea (a photo or clip cut out and taped, the speaker's words handwritten under it).
- Headlines as `impact` with `look: "stack"`: rows pop in one at a time, like strips of paper.
- A full-screen `scene` `card` on the paper board (bg #E8DCC6) for the one line to remember.
- Sounds: paper-flip / paper-riffle on each cut-out (cc0), no whooshes. Bed: a-baby-story (acoustic).

## Example beats

```json
[
 {
  "type": "polaroid",
  "src": "assets/ins/photo1.jpg",
  "caption": "ต้นทุนความรัก",
  "at": 0.8,
  "to": 4.0
 },
 {
  "type": "impact",
  "look": "stack",
  "at": 4.6,
  "to": 7.0,
  "text": "ความลุ้น|{ความรอคอย}",
  "role": "topic"
 },
 {
  "type": "scene",
  "kind": "card",
  "at": 7.6,
  "to": 10.6,
  "lines": [
   {
    "text": "อย่ารีบ",
    "at": 7.8,
    "size": 120,
    "color": "#111111"
   }
  ],
  "pill": {
   "text": "ทีละนิด",
   "at": 8.6
  }
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
