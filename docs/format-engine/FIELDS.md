# format_spec.py fields

All times in seconds, positions and sizes in % of the frame (x from the left, y from the top).

- `seconds`, `w`, `h`: length and frame size.
- `cuts`: `times` of hard cuts and jump cuts (a frame-difference spike against its own neighbourhood), `n`, `per_min`,
  `shot_median` and `shot_p90` (shot lengths), `first` (the first cut). On TadClip's own reels this finds every jump cut
  at the right frame; about 1 detection in 10 is another visual change (a punch-in zoom, a card appearing).
  Since version 2: `shot_cuts` (the face box itself changes: a cut of the speaker's shot, or a cut away to full-screen
  footage) and `insert_changes` (a change elsewhere in the frame: a panel, a screen recording, a card), with
  `shot_cuts_per_min`; `shot_median` / `shot_p90` are measured between shot cuts.
- `text`: on-screen text read with macOS Vision at 2 frames a second (Thai and English; Vision misreads handwriting and
  stylised Thai, so treat the words as approximate and the timing and position as reliable).
  - `chrome`: text on screen for 40 %+ of the reel at one place (a logo, a handle, a tagline): `[text, x, y]`.
  - `list`: text events (lines shown together and stacked): `t0`, `t1`, `text`, `rows`, `x`, `y`, `line_h` (the
    biggest line's height), `zone` relative to the face (`above`, `face`, `chest` = up to 25 % below the chin, `lower`,
    `no-face` when no face is on screen), `plate` (flat colour behind the text, empty = over the footage), `letters`.
  - summary: `events`, `share_of_time` (time with any text on screen), `first_seen`, `line_h_median`, `zones` (share of
    text time per zone), `rows_median`, `seconds_median` (how long an event stays), `gap_median` (start to start).
  - Footage that contains text (a whiteboard, a screen) shows up as events too.
- `face`: `share` of sampled frames with a face, median `top`, `bottom`, `cx` and `height`.
- `audio`: `lufs` (integrated loudness), `quiet_share` (below -35 dB for 0.35 s+), `pauses_per_min`, `longest_pause`.
