# Life in weeks · ชีวิตเป็นสัปดาห์

A span of time as a grid of dots, one per week; the part already lived (or the part that matters) fills in.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Life in weeks"). The preset is `styles/life-in-weeks.json` (`"style": "life-in-weeks"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- A `scene` `weeks`: `title`, `sub`, `total` (dots, default 4,160 = 80 years), `filled`, `fillAt`, `fillDur`, `cols` (52).
- Use it once per reel, on the line about time ("80 ปี", "ทุกสัปดาห์"); the speaker before and after.
- Sounds: a riser under the fill (automatic). Bed: silent-descent.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "weeks",
  "at": 0.8,
  "to": 6.0,
  "title": "อยู่ด้วยกัน 80 ปี",
  "sub": "4,160 สัปดาห์ · หนึ่งจุด = หนึ่งสัปดาห์",
  "filled": 1300,
  "fillAt": 1.6
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
