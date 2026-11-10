# The format engine: read, save, fit, score

The method has four steps, and each step has one agent. A **reader** turns a creator's measured reels into
observations. A **spec-writer** turns those observations into a saved format (`format.schema.json`). A **fit-checker**
decides which parts of the format suit a new raw talking-head clip and sets the reel.json levers. A **critic** measures
the finished render and scores it against the format.

Notation: `cuts.per_min` and similar names are fields of a `format_spec.py` spec (`inputs/FIELDS.md`). `verdict.y`
and similar names are reel.json levers (`inputs/reel-json.md`). Positions are % of the frame: y is measured from the
top, and on a 1080x1920 render `y_px = y% × 19.2` and `x_px = x% × 10.8`. Reasons are cited as [S1]..[S13], listed in
`SOURCES.md`.

## 0. Ground rules for every step

1. **Numbers describe *when* and *where*. The contact sheet shows *what*.** The spec gives reliable timing and
   position. Text content is approximate: Vision misreads Thai and stylised type. Every claim about a device needs both
   a number (time, y, line_h) and a frame on the sheet that shows it.
2. **The unit is a format, not a creator.** One creator can run several series. Cluster the reels first (R1). Average
   only inside a cluster.
3. **Rates are per minute, and layouts are shares of time.** Reels range from 13 s to 67 s, so a count per reel is
   not comparable across reels.
4. **Mark every value with how you know it.** `measured` means a spec field. `looked` means read off the contact
   sheet. `derived` means computed from the spec's lists. Never present a looked value as measured.
5. **Leave unknowns unknown.** Animation, sound effects, music, transitions and word-by-word caption motion cannot be
   seen in one still per shot. Write `unknown`. TadClip's defaults apply until a person watches the reel.

---

## 1. READ (reader agent)

Input: each reel's spec JSON and contact sheet. Output: a reading table per reel with one row per observation (value,
basis, evidence times), plus the cluster decision.

### R1. Cluster the reels before reading them together
- Compare the reels on: frame size (`w`,`h`), `face.share`, recurring `text.chrome` items (same text at the same x,y),
  recurring `text.list` events (same y ±3 and similar `line_h` at a similar `t0`), and the layout on the sheet.
- A reel joins a cluster when it shares **two or more devices** with the cluster. A reel that shares none becomes a
  separate variant or is excluded, and the reason is written down. Examples from the inputs:
  - `itstundeanthony-C1-K1UfM_eB` (360x640, typed code panels down the left, no "Fact or Hype" items) is excluded from
    his Fact-or-Hype format. The other three share the title pill at y≈17.5, the "IS IT FACT OR HYPE" stack, and the
    FACT/OR/HYPE chrome at y≈50–52.
  - `kamchai-DeQr_7OKgcZ` (`face.share` 0, 12.8 s, a phone filming a monitor with a 4-row Thai title in `text.chrome`)
    is a different POV series. It is excluded from his split-screen format.

### R2. Rhythm: cuts
- Read `cuts.per_min`, `cuts.shot_median`, `cuts.shot_p90` and `cuts.first`. Keep the median and the p90, not just
  the rate. Edit rhythm is a distribution: neighbouring shot lengths correlate, and editors use the long tail on purpose
  [S1].
- **Classify the cuts on the sheet.** Each frame is a shot start, so compare it with the frame before it:
  - *speaker cut*: same layout, the speaker's framing or pose jumps (a jump cut or punch-in → `takes`, `zoom.snaps`);
  - *layout change*: split ↔ full speaker ↔ full cutaway (→ `broll`, `mode`);
  - *inset change*: only a panel or inset changes content, and the speaker stays still (the detector fires on the panel
    and it is not an edit of the voice).
  Write the share of each kind as `looked`. Example: in the three Fact-or-Hype reels most detections after the hook
  are inset changes, so `cuts.per_min` (13–21) overstates how often the voice is cut. In kamchai's reels, layout changes
  and B-roll cuts inside the top half drive the 36–46/min rate.
- On TadClip's own reels about 1 detection in 10 is not a cut (FIELDS.md). On creator reels with screen panels the error
  is much larger, and the classification above is how you correct for it.
- `cuts.first` describes the hook only if the first frames show the speaker. If the hook is an inset clip, its cuts
  belong to the clip.

### R3. Text: split the creator's own graphics from text in the footage
`text.share_of_time` and `text.zones` count every word Vision sees, including screens, GitHub pages and app UIs. Sort
every `text.list` event into **own graphic** or **footage text** before using it.

| signal (from the event) | own graphic | footage text |
|---|---|---|
| `rows` | 1–3 | often 5–60 |
| `line_h` | ≥ 1.8 % (captions), ≥ 3.5 % (titles, punch words) | < 1.2 % |
| `letters` | near-white `#F8F8F8`, near-black `#080808`, or one saturated accent (`#F8E808`, `#E82848`) | many greys `#383838`…`#C8C8C8` |
| `plate` | none, or one flat colour (`#FEFEFE` pill, `#FAF441` label) | many near-identical UI shades |
| position | repeats at the same x,y across reels | drifts with the screen |

Then give each own-graphic event a **role** and record its `y` range, `line_h` range, `rows`, `plate`, `letters`,
duration (`t1−t0`) and anchor time:
- **caption**: speech-synced phrases at a fixed y, 1–2 s each, gaps ≈ durations;
- **punch word**: 1–2 rows, `line_h` ≥ 5 %, 1–2 s, on a spoken keyword (signalling [S3]);
- **title / hook card**: `t0` = 0, held 2–9 s;
- **label**: a short line on a plate above or under the head;
- **persistent bar / chrome**: in `text.chrome`, or one event that lasts to the end;
- **CTA**: in the last ~4 s (a comment keyword, a handle).
Vision words are approximate. Match a role to speech by timing, not by spelling.

### R4. Read zones against the face, then in absolute y
`text.zones` is relative to the face, so it moves when the face moves. When `face.top` > 40 (the speaker pushed into
the lower half by a split), a caption on the seam at y≈50 counts as `above`. That is why kamchai's `above` share is
0.74–0.76. Always record each role's absolute `y` too. Scoring uses absolute y; zones are used only to check the face.

### R5. Face and layout
- `face.share` < 0.95 → full-frame cutaways take about `1 − face.share` of the time.
- A `face.top` median well below the frame's centre band (> 40) or a `face.cx` far off 50 (> 58 or < 42) points to a
  split or a side-by-side inset. Confirm it on the sheet.
- From the sheet, record the **layout per sampled shot**: `full-speaker`, `split` (where the seam sits), `panel`
  (a box over the lower half), `inset` (another video beside the face), `full-cutaway`. Weight each shot by its length
  (the next frame's start time minus its own) to estimate each layout's **share of time** (`looked`), and note how long
  each layout block lasts before the next change.

### R6. Audio
- `audio.pauses_per_min`, `audio.longest_pause` and `audio.quiet_share` show how tightly the voice is cut. Near 0 means
  every breath is removed → tight `takes` a/b padding and few `hold`s.
- **Do not save `audio.lufs` as a style.** Platforms normalise loudness on delivery, as broadcast does under
  EBU R 128 [S11]. A downloaded reel's −14 LUFS tells you about the platform, not the creator. TadClip's −16 voice
  target stays.

### R7. How to look at a contact sheet (what numbers cannot give)
For each frame, write one line: layout, where the speaker's head is, every own graphic with its style, and any
sticker or logo. Look specifically for:
1. **Type style**: weight, italic, case, outline or shadow, a plate's shape (pill, box, torn paper), and which word
   carries the accent colour (Vision gives the colours; the sheet shows which word gets them).
2. **Plates Vision misses**: translucent dark strips show as `plate: []`. Kamchai's seam captions sit on one.
3. **Recurring treatments** (devices): a bar across the chest, a framed panel, a photo or logo beside the face, an
   inset clip of another video, an emoji next to a word, a handle sticker at the end. Write down which frame and what
   it does.
4. **Framing**: shot scale (face height ≈ `face.height`), the setting, whether the speaker moves between shots.
5. **The last frame**: a verdict, a CTA, an end card.
Things you cannot know from the sheet: entry/exit motion, sound, transitions between frames, per-word caption effects,
and anything shorter than one shot. Mark these `unknown`.

---

## 2. SAVE (spec-writer agent)

Input: the reader's tables for one cluster. Output: one JSON file valid against `format.schema.json`, plus a
one-paragraph reading.

### S1. Every numeric field is a range, with its source and lever
For each field, save `observed: [min, max]` across the member reels and an **accept** band that the fit and score
steps use:
`accept = [min − w, max + w]`, where `w = max(0.15 × |bound|, floor)` for magnitudes (times, durations, rates,
sizes). Positions (x, y, face top/bottom/cx) and shares are not ratio scales, so they get the floor only.
Floors come from how the measurement is taken: **0.5 s** for text times (Vision samples at 2 fps), **0.25 s** for shot
lengths, **3 %** for positions, **0.5 %** for `line_h`, **0.05** for shares, **3** for per-minute rates, **1** for `rows`.
Clamp shares to [0, 1] and `rows` to at least 1. Round to 2 significant decimals. With **n = 1** use ±25 % and set `confidence: "low"`. Each field also stores `n`, `basis`
(`measured | looked | derived`), `source` (the spec path, or `contact sheet`) and `lever` (the reel.json path it sets,
or `none: <why>`).

### S2. What to save
- **rhythm**: `cuts.per_min`, `cuts.shot_median`, `cuts.shot_p90`, `cuts.first`, plus the looked cut-kind shares.
  Sets `takes` density, `zoom.snaps` and the `broll` / layout switches.
- **text roles** (R3): one entry per role, with `y`, `line_h`, `rows`, duration, `plate`, `letters`, `gap` (start to
  start) and the matching lever (`captions.*`, `impact` with `look`/`place`/`y`/`size`, `textfx`, `title`).
  `line_h` → size: Vision's box hugs the glyphs. For Latin type set the font `size` to about `line_h% × 19.2 × 1.2` px.
  For Thai use `× 0.8`, because the box includes the stacked vowels and tone marks. Both factors are starting points:
  check the first render's spec and correct them (C5).
- **text totals**: `text.seconds_median`, `text.gap_median`, `text.rows_median`, `text.line_h_median`. Compute them
  from own graphics only (derived) whenever footage text inflates the raw values. Save the raw value too, as a note.
- **layout**: `face.top`, `face.height`, `face.cx` and `face.share` → `zoom.base`, `zoom.faceAt`, `broll.shift`; the
  layout shares (looked) → how much of the reel is `broll` split, panel or full.
- **audio**: `audio.pauses_per_min` and `audio.longest_pause` → `takes` padding and `hold`.
- **devices** (S3) and **structure**: hook (from 0 to the first layout change, or to the end of the title card),
  body, end.

### S3. Devices
A device is a recurring treatment with a job. For each device save: `id`; `what` (in words); `when` (an `anchor`, one of
`hook | spoken-cue | section-change | persistent | end`, plus a time range relative to the start or the end and the
cue that triggers it); `where` (y/x ranges); `seen_in` (k of n reels, with evidence times); `role`
(`signature` if k/n ≥ 2/3, otherwise `optional`); `lever` (the beat type and fields); `needs` (the material the
new clip must have, e.g. a screen recording, a product name, an offer).

### S4. What not to save
Topic words, product names, `audio.lufs`, raw footage-text shares as style, and anything `unknown`. Save the
*function* ("a product name labelled on the B-roll in the hook"), not the content ("Ltx").

---

## 3. FIT (fit-checker agent)

Input: a saved format and the new raw clip (transcript words with times, `face.json`, duration, measured pauses, the
material the user has: screen recordings, product names, an offer). Output: a fit table, then a reel.json fragment.

### F1. Decide per field and per device: **keep · adapt · drop · ask**
| test | what you compare | fails → |
|---|---|---|
| **material** | the device's `needs` vs what the clip and user have (a verdict needs a claim that the speaker tests; a panel needs a screen recording; a comment-keyword CTA needs something to send) | drop, or ask the user. Never fake a screen recording or a product. Stock B-roll may stand in for *illustrative* footage only (`broll_fetch.py`) |
| **spoken cue** | does the transcript contain the cue the device lands on (a number, a product name, a "not X", a question)? | drop that instance; keep the device for the cues that do exist |
| **geometry** | the device's y-range vs the new clip's face box (from `face.json` after `zoom.base`). Faces draw the first fixations [S2], so own graphics must not cover the face (`zone` = `face` share ≤ the format's own share) | adapt: move it (`y`, `place`, `impact.top`), change `zoom.faceAt`, or for splits change `broll.shift` |
| **density** | per-minute rates from the format × the clip's length | keep the rates, not the counts. If the clip is outside `seconds.accept`, flag the length and do not stretch or crush the content |
| **pace** | `cuts.per_min.accept` vs what the speech allows | reach the rate with `zoom.snaps` (reframes on sentence starts) and layout switches. **Never drop words just to hit a cut rate** |
| **readability** | each text role's duration vs the words it holds (F2) | adapt: split the text into more events, cut words from the *on-screen* text (not the speech), or lengthen `to` |
| **language** | Thai or English (F3) | adapt the sizes and line breaks |
| **platform** | own graphics inside the safe area: `platform`, `layout.capBottom`, never below y 1470 for cards (builder rule) | move them up |

### F2. Reading-time floor (both languages)
- Every own-graphic event stays up for at least **max(1.0 s, 0.3 s per word)**. The builder enforces the same floor
  for `textfx`. Netflix's minimum is 5/6 s [S7].
- **Thai**: at most **17 characters per second** for adults and **35 characters per line**, not counting tone marks
  and upper or lower vowels; two lines at most, one preferred [S6]. English: aim under 3 words/s for captions.
  TikTok's own "5–10 words per second" [S9] is an upper bound for a glanceable overlay that repeats the speech, not a
  target.
- A caption is not a transcript of everything. Short on-screen keywords that sit next to what they refer to help, but
  full redundant text competes with the picture in fast material [S3]. Same-language captions improved comprehension
  without a significant rise in measured load in lecture studies [S4], so **captions stay on by default** (and
  WCAG 1.2.2 asks for them [S12]) unless the format puts its own text where captions would go.

### F3. Thai specifics
- Thai has no spaces between words, and inserted spaces measurably help Thai readers recognise words [S5]. Break lines
  and rows only at phrase boundaries. Write the break as `|` (impact rows) or let the builder break at spaces.
  `fixes`/`phrases` must not glue phrases together.
- Thai rows run longer than English. When a role's measured `line_h` would push a row past ~900 px wide, split it into
  two rows (stair/stack/headline `|`). Do not shrink below the builder's 64 px warning.
- Fonts: Kanit / Kanit Medium for heavy display rows, Prompt or Anuphan for captions. Choose by the observed weight on
  the sheet.

### F4. Output
A table with one row per field and device: `format range → clip value → decision → lever = value → reason`. Then the
reel.json fragment. Mark every `drop` and `ask`, so the critic does not penalise what the fit removed.

---

## 4. SCORE (critic agent)

Input: the format, the fit table, and the finished reel's spec JSON + contact sheet (run `format_spec.py` on the
render). Output: a score card, then at most **three** fixes, each naming a lever and a value.

### C1. Gates (checked first, apply to every format)
A reel that fails a gate is "not shippable", whatever its score:
1. **Face covered**: own-graphic events with `zone` = `face` add up to more than the format's own `face` share + 0.05,
   checked on the sheet (the speaker's eyes and mouth hidden by a card) [S2].
2. **Unreadable**: any own-graphic event shorter than max(1.0 s, 0.3 s/word); Thai > 17 cps or > 35 chars/line [S6][S7].
3. **Out of the safe area**: an own card or caption with `y` > 76.5 % (1470 px) or under the top chrome. Check against
   the platform preview the builder applies (`platform`).
4. **Two caption layers**: two speech-synced text roles on screen at once (`captions` + burned-in, or captions not
   hidden under an `impact`).
5. **Low contrast**: small text (`line_h` < 3 %) with no plate and no outline over busy footage. WCAG's 4.5:1 for text
   and 3:1 for non-text [S12]. Measure the letter colour against its plate, or look for an outline.
6. **Flashing**: more than 3 flashes in one second (glitch exits, strobe captions) [S12].

### C2. Field scores
Score each saved field the fit did not drop: inside `accept` → 1. Outside → `max(0, 1 − d / width)`, where `d` is the
distance to the nearer edge and `width = accept[1] − accept[0]`. Use the same derived definitions as the format (own
graphics only, the same layout shares). Group and weight the scores:

| group | fields | weight |
|---|---|---|
| devices | each signature device present at its anchor, in its y-band, on the sheet (1/0; optional devices only count if the fit kept them) | 0.40 |
| rhythm | `cuts.per_min`, `cuts.shot_median`, `cuts.shot_p90`, `cuts.first`, cut-kind shares | 0.25 |
| text | roles' `y`, `line_h`, duration, `gap`; `text.seconds_median`, `text.gap_median`; first own text at `first_seen` | 0.20 |
| layout & voice | `face.top`/`height`/`cx` per layout, layout shares, `audio.pauses_per_min`, `audio.longest_pause` | 0.15 |

Devices carry the most weight because they make a format recognisable. Rhythm comes next.
`score = Σ group weight × mean(group)`. Report: ≥ 0.85 *on format*, 0.70–0.85 *close*, < 0.70 *off format*.

### C3. The hook gets a separate check
Platforms judge a short video in its first seconds. TikTok asks for the proposition within the first 3 s and the hook
within the first 6 s [S9]. YouTube's retention report shows where viewers drop, and its own guidance is to experiment
with the opening [S10]. Separately check that the first 3 s show the format's hook devices (title card, inset, split)
and that the first own text appears at the format's `text.first_seen` (usually 0.0). Retention cannot be measured from
the file, so the critic never claims an outcome; it reports conformance.

### C4. Fixes
Write the three largest weighted losses as `lever = value` (e.g. `"captions.onlyInSplits": true`, `zoom.snaps` on
these sentence starts, `impact.y` 1230). Never suggest something the fit marked `drop`.

### C5. Calibration on TadClip's own reels
Before trusting the critic, run it on `kg01k`, `kg03` and `clinic-after`, where the edit is known. For example,
`kg01k` scored against kamchai's split-screen format: the layout matches (top-half B-roll, a white phrase with the
keyword in yellow on the seam, the speaker in the lower half: `face.top` 62.3). But `cuts.per_min` 27.9 is below
accept [31.0, 52.9] (score ≈ 0.86), and `text.gap_median` 2.5 s is above accept [1.0, 2.0] (score 0.5). It also has a
persistent top-left chrome that the format does not have. The critic should say: "close; cut more often, put own text
on more of the sentence starts". If the critic disagrees with what the sheet plainly shows, fix the critic first.

---

## Appendix A. Field → lever map (the levers this method sets)

| measured | lever |
|---|---|
| `cuts.per_min`, `shot_median`, `shot_p90` | `takes` (a/b padding, how many), `zoom.snaps`, `zoom.pushes`, `broll` switches |
| `cuts.first` | the first `takes` boundary or the first `zoom.snaps` time |
| `audio.pauses_per_min`, `longest_pause` | `takes` b-padding, `hold` |
| `face.top`, `face.cx`, `face.height` | `zoom.base`, `zoom.faceAt`, `zoom.origin`, `broll.shift` |
| caption role `y`, `line_h`, plate | `captions.style` (`mini`, `house`, `pill`, a template), `captions.y`/`splitY`, `size`, `strip`, `onlyInSplits` |
| punch-word role | `impact` (`look: stack/headline/stair`, `place`, `y`, `size`, `impact.color`) or `textfx` |
| title / hook role | `impact look: pill/qcard/headline`, `title`, `textfx kind: hook` |
| persistent bar | `verdict` (checkbox bar), `chrome` |
| inset / panel | `broll mode: panel` (`box`, `frame`), `polaroid` |
| split | `broll mode: split` (`h`, `shift`), `captions.splitY` |
| logos / icons | `logo`, `chips` |
| CTA | `cta`, `linecta`, `endcard` |

## Appendix B. Known blind spots
- Animation, sound, music, transitions: `unknown` until someone watches the reel.
- Vision's text reading is unreliable for stylised Thai and for handwriting, so trust its timing and position over the
  words.
- One frame per shot: a card that appears and leaves inside one shot may show only in `text.list`.
- `cuts` on reels with screen panels: classify them (R2) before using them.
- Two reels (kamchai) or three (itstundeanthony) only bound the format loosely. Each new reel from the creator should
  re-run R1 and S1 and widen or narrow the ranges.
