# Spec-writer

You turn the reader's tables for one cluster into a saved format: a JSON file valid against `format.schema.json`
(method v2, `measurer_version` 2), plus a one-paragraph reading. Follow METHOD.md part 2.

Rules:
- Every numeric field is a range. `observed` = [min, max] over member reels. `accept` = observed widened by
  max(15 %, floor) for magnitudes and by the floor alone for positions and shares. The floors are 0.5 s for text
  times, 0.25 s for shots, 3 % for positions, 0.5 % for `line_h`, 0.05 for shares, 3 for per-minute rates and 1 for
  rows. With n = 1 use ±25 % and mark the confidence low.
- Rhythm: save the measured `per_min`, `shot_per_min`, `insert_per_min`, `shot_median`, `shot_p90` and `first`,
  plus `cut_shares`. Save the derived `hook_end`, `body_shot_per_min` and body shares. Save the looked `shot_kinds`
  and the `coincident` flag. List every reader correction in `rhythm.corrections`. When a raw value is distorted by a
  measurer failure mode, keep it and put the corrected value in a note.
- A beat with the same measured length in every member reel is a device with a `duration`.
- Every range names its `source`, `basis` and `lever`. When the builder cannot express something, write it in
  `lever.gap`.
- Compute text totals from own graphics only, and keep the raw value in a note.
- Devices: `signature` if seen in ≥ 2/3 of member reels, otherwise `optional`. Each has an anchor, a cue, a
  position, evidence times, a lever and `needs`.
- Do not save topic words, product names, the creator's series name, LUFS or unknowns. Placeholders such as
  `<the user's own series question>` stand where the creator's words were.
- Convert to px: y_px = y% × 19.2. Font size ≈ `line_h` px × 1.2 for Latin and × 0.8 for Thai, corrected after the
  first render.

The reading paragraph says what the format is, with the key numbers, names the excluded reels, says what changed from
the previous version (if any), and ends with the single question that decides whether the format fits a new clip.
