# Format engine: architecture

Goal: from an Instagram handle, a TikTok, a YouTube Short or a pasted link, a **measured** creator format that TadClip
applies to the user's own clip, with no Hypit text or code in the product. Numbers first, a model's reading second.

```
 handle / links ──► SCOUT ──► reels (mp4) + metadata
                                  │
                                  ▼
                            MEASURER  scripts/format_spec.py ──► spec.json + contact sheet per reel
                                  │                               (cuts, text events with zone/size/colour,
                                  ▼                                face, loudness, pauses)
                            READER   (Claude, briefs/reader.md) ──► what recurs across the reels and why it works,
                                  │                                  from the specs and the sheets
                                  ▼
                            SPEC WRITER (briefs/spec-writer.md) ──► styles/creator-<handle>.json  (format.schema.json:
                                  │                                  ranges, devices, each mapped to a reel.json lever)
          the user's clip ──►     ▼
          (spec of the raw  FIT CHECKER (briefs/fit-checker.md) ──► what transfers to THIS clip, what is dropped and why
           take + transcript)     │
                                  ▼
                            TadClip's build (build.mjs, reel.json) ──► preview
                                  │
                                  ▼
                            CRITIC  (briefs/critic.md + format_spec.py on the preview) ──► score vs the saved format:
                                                                        in range / out of range per field; fix list
```

## The roles

| role | what it is | input | output | deterministic? |
|---|---|---|---|---|
| scout | `creator_study.py` today; product: official APIs first (Instagram Graph API Business Discovery on the user's own professional account for the list and view counts; YouTube Data API for Shorts), links the user opens in their own browser for TikTok and anything an API won't give | handle or links | reels + metadata (views, dates) | yes |
| measurer | `scripts/format_spec.py` | one reel | `spec.json`, sheet | yes |
| reader | a Claude agent with `briefs/reader.md` | 3-5 specs + sheets of one creator | a reading: recurring numbers, recurring devices, the hook | no (model) |
| spec writer | a Claude agent with `briefs/spec-writer.md` | the reading + specs | `styles/creator-<handle>.json`, schema-valid | no, but validated |
| fit checker | a Claude agent with `briefs/fit-checker.md` | the saved format + the raw take's spec and transcript | keep / adapt / drop per device, with the reason | no |
| critic | `format_spec.py` on the preview + a Claude agent with `briefs/critic.md` | the saved format + the preview's spec | per-field in/out of range; one fix list | the measurement is |

Why this split: the numbers (rhythm, text size and place, loudness) are measured, so two runs agree and a test can
check them; the model only does what needs judgment (why a device works, whether it suits this clip). The critic closes
the loop with the same measurer, so "it looks like their format" becomes "12 of 14 fields in range".

## Where it sits in TadClip

- Replaces, for the paid build: `vendor/hypit/` and the two guides `recipes/clone/README.md` sends the agent to.
  The route stays the same for the user (`ตัดต่อคลิปนี้ให้เป็นสไตล์ @creator`).
- Reuses: `creator_study.py` (fetch), `face_track.py` (YuNet), `ocr_text.js` (Vision), `own_brand.py` (colour maths),
  `styles/creator-*.json` (the overlay format build.mjs already applies).
- New: `scripts/format_spec.py`, `docs/format-engine/` (method, schema, briefs: written in the clean room, see
  PROVENANCE.md), `tools/format-eval/` (scoring), `tools/cleanroom/guard.py`.

## Sources, safely

- Product default: official APIs + the user's own browser. No bundled bulk downloader. A link the user pastes is
  fetched once, for their own study, on their machine.
- Instagram Business Discovery needs the user's Instagram professional account connected (Meta app review for a
  public app). Reels whose owners turned off downloads come without a media URL: the reader then works from the
  user's browser (screen capture of the reel playing) or skips it.
- TikTok: no public API for other creators' videos; links the user opens and records in their own browser.

## What's built in this PR, and what isn't

Built: the measurer (`format_spec.py`), the clean room and its guard, the clean-room method/schema/briefs and two
saved formats (out of the clean room, copied in with provenance), the evaluation tools and the first scores.
Not built: the official-API scout (needs a Meta app), wiring the fit checker and critic into `recipes/clone`, removing
`vendor/hypit/` from the paid build. Those follow the scores in EVAL.md.
