# Animated film · ฉากหนังแอนิเมชัน

Saturated, painterly stills like an animated film's backgrounds, a slow camera drift, warm serif subtitles low on screen.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Animated film"). The preset is `styles/animated-film.json` (`"style": "animated-film"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- Long `scene` `image` beats (4–6 s) with `zoom: [1.15, 1.0]` (a drift back) and `captions: true` so the subtitle stays.
- Subtitles: the `mini` caption style in Pridi, low (y 1500), like a film's.
- No impact cards: the picture carries the line. Bed: vastness or a-new-life.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "image",
  "src": "assets/ins/photo1.jpg",
  "at": 0.6,
  "to": 6.0,
  "zoom": [
   1.15,
   1.0
  ],
  "captions": true
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
