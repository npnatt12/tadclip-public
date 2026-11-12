# Motion light · ตัวอักษรขาวสว่าง

Clean white screens of bold words that move in line by line, one keyword in a soft blue.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Motion light"). The preset is `styles/motion-light.json` (`"style": "motion-light"` in reel.json),
an overlay on clean: everything not listed here follows clean's rules.

## Grammar

- `scene` `kinetic` on white: the words land as spoken; `*keyword*` in the soft blue.
- The Clean OS rules otherwise: lots of white, no plates. Sounds: minimal. Bed: digital-clouds.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "kinetic",
  "at": 0.8,
  "to": 6.4,
  "text": "อย่ารีบ *build* มันขึ้นมาทีละนิด"
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
