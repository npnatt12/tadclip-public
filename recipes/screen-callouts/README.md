# Screen callouts · ชี้จุดบนหน้าจอ

A phone screen (chat, app, post) rises in; the part that matters is circled and labelled.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Screen callouts"). The preset is `styles/screen-callouts.json` (`"style": "screen-callouts"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- A `scene` `device`: a phone frame with an image (a screenshot) or a mini chat (`lines: [{text, at, me}]`).
- Then an `impact` naming what to look at, or a `chips` row for the handle / button.
- Sounds: notification-2 per bubble, click-1 on a tap. Bed: digital-clouds.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "device",
  "at": 0.6,
  "to": 6.0,
  "label": "LINE",
  "lines": [
   {
    "text": "สนใจคอร์สออนไลน์ครับ",
    "at": 1.0,
    "me": true
   },
   {
    "text": "ปรึกษาปัญหาความรัก ทักมาได้เลยครับ",
    "at": 2.2
   }
  ]
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
