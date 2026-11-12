# Notes + bubble · โน้ต + วงหน้า

The idea written out like a dark notes app, word by word in time with the voice; the speaker in a small round bubble.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ Notes + bubble"). The preset is `styles/notes-bubble.json` (`"style": "notes-bubble"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- A `scene` `kinetic` on #151515 with `pip: true` (the speaker in a circle, `pipX`/`pipY` to place it).
- Mark the one word to remember as `*keyword*` (gold); fillers as `_filler_`.
- Sounds: soft ticks only. Bed: lo-fi-02.

## Example beats

```json
[
 {
  "type": "scene",
  "kind": "kinetic",
  "at": 0.8,
  "to": 6.8,
  "text": "อย่ารีบ build มันขึ้นมา *ทีละนิด* ให้เค้าลุ้นไปเรื่อยๆ",
  "pip": true
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
