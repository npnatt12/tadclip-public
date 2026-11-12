# Cinematic doc · สารคดีภาพยนตร์

A documentary grade on the speaker (cool shadows, warm skin, grain, vignette), serif italic words stacked one by one.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Cinematic doc"). The preset is `styles/cinematic-doc.json` (`"style": "cinematic-doc"` in reel.json),
an overlay on cinematic: everything not listed here follows cinematic's rules.

## Grammar

- The cinematic preset's grade, grain and vignette on the speaker, all the way through.
- Points as `impact` in the `seoul` look (serif italic, no plate), one to three words each.
- A `scene` `sentence` on black for the line that closes the argument.
- Sounds: restrained; one low boom at most. Bed: silent-descent.

## Example beats

```json
[
 {
  "type": "impact",
  "look": "seoul",
  "at": 0.8,
  "to": 3.2,
  "text": "ความลุ้น",
  "role": "note"
 },
 {
  "type": "scene",
  "kind": "sentence",
  "at": 4.0,
  "to": 8.6,
  "lines": [
   "ความรอคอย",
   "สะสมเป็น"
  ],
  "hero": {
   "text": "โดพามีน",
   "at": 6.8
  }
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
