# Vox · ภาพแกะลาย + เลนส์

Explainer-documentary look: engraved/halftone stills, a lens circle that isolates a detail, serif italic captions.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Vox"). The preset is `styles/vox.json` (`"style": "vox"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- Stills as full-screen `scene` `image` with the engraved grade (grayscale + sepia + contrast) and a slow push.
- The point of each still: an `impact` in the `seoul` look (serif italic, no plate).
- Halftone over the speaker plate (`look.shader: ["halftone"]`) so the face matches the stills.
- Sounds: restrained (paper, a low boom on the reveal). Bed: drawing-the-sky.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "image",
  "src": "assets/ins/photo2.jpg",
  "at": 0.8,
  "to": 4.2,
  "zoom": [
   1.0,
   1.12
  ]
 },
 {
  "type": "impact",
  "look": "seoul",
  "at": 4.8,
  "to": 7.4,
  "text": "คนที่รู้วิธี",
  "role": "note"
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
