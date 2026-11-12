# Paper explainer · ค้นหา + เผยคำตอบ

Words resolve on warm paper, one idea per screen, like a hand-made explainer.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Paper explainer"). The preset is `styles/paper-explainer.json` (`"style": "paper-explainer"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- `scene` `word` beats on the mesh-calm look (pastel, dark ink; warm-grain was too dark for dark ink, 11-12): 1–3 words that resolve from blur.
- Between them, the speaker with ClubGig captions.
- Sounds: paper-flip on each word. Bed: forest-mist-whispers.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "word",
  "at": 0.8,
  "to": 4.0,
  "text": "หาคนที่ใช่",
  "ink": "#222222"
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
