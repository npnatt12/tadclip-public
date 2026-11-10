# Changes from method v1 to v2

## Method (METHOD.md)
- **Cut kinds are now measured.** R2 reads `cuts.shot_cuts`, `cuts.insert_changes` and `shot_cuts_per_min`. The shot
  and insert shares replace v1's looked speaker/layout/inset shares. The sheet now only names *why* the speaker's shot
  changed (speaker / layout / cutaway, R2.4).
- **New: the hook is split from the body (R2.2).** A measured `hook_end`, a derived `body_shot_per_min` and a derived
  `body_shot_median`. The hook and body run different rhythms in both formats.
- **New: an audit of measurer v2's failure modes (R2.3)**, each found on these sheets: a second face in an inset turns
  its cuts into "shot cuts" (De1zlGniBQp, DfIM7fyIZXI); own graphics appearing count as "insert changes"
  (DeUOm5syXua); a cut to full-frame footage can be labelled an insert (Detm2VPS1Mp 7.67 s).
- **New: coincident cuts (R2.5)** and the fit test that uses them: when a format cuts the speaker and the panel on the
  same frame, panel clips start on take boundaries.
- **The fit separates two pace levers.** Take boundaries and snaps set the shot-cut rate, and clip changes set the
  insert rate.
- **C5 calibration redone with v2.** `kg01k` vs kamchai: the insert rate is on format (9.6/min), the shot-cut rate is
  not (18.3 vs accept 25.4–38.3). The fix is to cut the speaker more often, not to add B-roll.
- R1 also checks the uploader account (study file). R3 warns that fixed-position background objects are not graphics
  (kg03 "Tlia"). R5 handles sheets that stop before the reel ends.
- New sources: Smith & Henderson on edit blindness [S19], YouTube Shorts "viewed vs swiped away" [S16].

## Schema (format.schema.json)
- `measurer_version` is required. `reels[].account` and `reels[].sheet_covers_to` are added.
- `rhythm` now requires `shot_per_min`, `insert_per_min` and `cut_shares` {shot, insert}. Optional:
  `hook_end`, `body_shot_per_min`, `body_shot_median`, `cut_shares.body_*`, `shot_kinds` {speaker, layout, cutaway},
  `coincident` and `corrections`. v1's `cut_kinds` is removed.
- `text.own_events_per_min` is added (used by the competitor comparison).

## Fact-or-Hype format (corrected against specs2)
- **Contradicted in v1:** "most detections after the hook are inset changes; the voice is cut far less often than
  the number suggests" (`cut_kinds.inset` 0.6–0.9). In v2 the body shares are shot 0.90–0.93 and insert 0.07–0.10. On
  the sheets the speaker's pose jumps at nearly every cut. The body is jump-cut 11.1–14.2 times a minute (median shot
  2.7–5.0 s), and each jump cut also starts a new panel clip.
- `shot_median` / `shot_p90` are re-measured between shot cuts: 1.95–4.33 / 5.64–9.49 (v1 1.93–3.28 / 5.31–9.47).
- **New measured device:** the question shot lasts **1.97 s** in all three reels (hook end to the next shot cut).
- **New device:** `source-page-first`. The first 1–3 panel shots are the claim's own page, unframed (2.4–6 s), before
  the teal-framed test. v1 called the whole panel teal-framed.
- `hook-stickers` (optional, 1/3) becomes `claim-tags` (signature, 2/3): DfIM7fyIZXI's inset also carries tags (paid
  → open source, a star counter, a product card). Whether they are his own graphics is marked unknown.
- Layout shares are now derived from measured times (inset 0.11–0.14, question shot 0.03–0.04, panel 0.82–0.86).
- Lever values no longer carry the creator's own words ("FACT/HYPE" become `<option A>/<option B>`).

## Kamchai split format (corrected against specs2)
- v1's even three-way cut mix (speaker 0.3–0.4, layout 0.25–0.35, inset 0.3–0.4) overstated B-roll swaps. In v2 shot
  cuts are 0.73–0.82 of detections and inserts 0.18–0.28. All four inserts in DeUOm5syXua are graphic onsets.
- New: shot-cut rate 29.9–33.3/min (body 30.3–37.7), and an insert rate of 6.6–12.6/min.
- `shot_median` / `shot_p90` re-measured: 1.38–1.57 / 2.91–3.37 (v1 1.2–1.4 / 1.97–2.79).
- The hook end is now explicit (2.5 / 7.67 s). Block lengths now come from layout shot-cut times (2.47–8.63 s).
- The excluded DeQr_7OKgcZ was posted from a different account handle (study file). The exclusion stands.

## Briefs
All four briefs are updated for v2. The fit-checker and spec-writer now forbid carrying the creator's words, series
name, logo, music or footage into lever values.
