# New background · เปลี่ยนฉากหลัง

The speaker cut out and placed in a new scene (a place, a colour field, a moving clip); light-wrapped and colour-matched.

Ask for it by name ("ตัดต่อคลิปนี้สไตล์ New background"). The preset is `styles/new-background.json` (`"style": "new-background"` in reel.json),
an overlay on clubgig: everything not listed here follows clubgig's rules.

## Grammar

- `cutout` beats with `fx: "bg-swap"` and `bg` = a still, a clip or two hex colours; one per section, 3–6 s each.
- Needs the person matte (`bash scripts/setup_matte.sh`, ~2.6 GB, once). Without it, use `bg-blur` or skip.
- Captions stay ClubGig. Bed: vastness (spacious). A whoosh on each swap.

## Example beats

```json
[
 {
  "type": "cutout",
  "fx": "bg-swap",
  "at": 1.0,
  "to": 4.0,
  "bg": "#1b2a4a,#d9a05b"
 },
 {
  "type": "impact",
  "at": 4.8,
  "to": 7.0,
  "text": "ลองนึกภาพ|ทริปแรกของเรา",
  "role": "topic"
 }
]
```

## Status

New 2026-11-12. Its first look comes from the README styles grid. The preset builds and renders
(`tests/render_styles.py`); judge it on a real reel and tune the preset like any other style.
Sounds and music are TadClip's own or CC0 (docs/THIRD_PARTY/audio.md).
