# 3-step lesson · บทเรียน 3 ขั้น

A lesson in three numbered steps over a flowing colour field, then back to the speaker for each explanation.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ 3-step lesson"). The preset is `styles/3-step-lesson.json` (`"style": "3-step-lesson"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- A `scene` `card` on a moving shader field (warp, Passion) listing the steps: `1 …`, `2 …`, `3 …` as lines.
- Then one `impact` per step while the speaker explains it, numbered the same.
- Sounds: a pop per line. Bed: happy-times.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "card",
  "at": 0.6,
  "to": 6.0,
  "y": 640,
  "lines": [
   {
    "text": "1 ยืดระยะเวลา",
    "at": 1.0,
    "size": 84,
    "color": "#FFFFFF"
   },
   {
    "text": "2 ให้เค้าลุ้น",
    "at": 2.4,
    "size": 84,
    "color": "#FFFFFF"
   },
   {
    "text": "3 ฉากที่ไม่มีวันลืม",
    "at": 3.8,
    "size": 84,
    "color": "#FFFFFF"
   }
  ]
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
