# The format engine: read, save, fit, score (version 2)

The method has four steps, and each step has one agent. A **reader** turns a creator's measured reels into
observations. A **spec-writer** turns those observations into a saved format (`format.schema.json`). A **fit-checker**
decides which parts of the format suit a new raw talking-head clip and sets the reel.json levers. A **critic** measures
the finished render and scores it against the format. Version 2 follows measurer version 2, which splits every cut
detection into `cuts.shot_cuts` and `cuts.insert_changes`. What changed from version 1 is listed in `CHANGES.md`.

Notation: `cuts.shot_cuts_per_min` and similar names are fields of a `format_spec.py` spec (`inputs/FIELDS.md`).
`verdict.y` and similar names are reel.json levers (`inputs/reel-json.md`). Positions are % of the frame: y is measured
from the top. On a 1080x1920 render `y_px = y% × 19.2` and `x_px = x% × 10.8`. Reasons are cited as [S1]..[S22] and
listed in `SOURCES.md` (S8 and S13 were looked for and not relied on).

## 0. Ground rules for every step

1. **Numbers say *when* and *where*. The contact sheet shows *what*.** The spec's timing and position are reliable.
   Its text content is approximate. Every claim about a device needs a number (a time, a y, a `line_h`) and a frame
   on the sheet that shows it.
2. **The unit is a format, not a creator.** Cluster the reels first (R1), and average only inside a cluster.
3. **Rates are per minute, and layouts are shares of time.** Counts per reel are not comparable across reel lengths.
4. **Mark every value with how you know it.** `measured` is a spec field. `derived` is computed from the spec's lists,
   such as a rate over part of the reel. `looked` is read off the contact sheet. Never present a looked value as
   measured.
5. **Measurement first, eyes second.** When the spec measures something (a cut kind since v2, a text time, a face
   box), use the number. Use the sheet to audit the number against the known failure modes (R2.3) and to name what the
   number cannot name.
6. **Leave unknowns unknown.** Animation, sound, music, transitions and per-word caption motion cannot be seen in one
   still per shot. Write them as `unknown`.

---

## 1. READ (reader agent)

Input: each reel's spec JSON and contact sheet, plus the study file (URL and uploader). Output: a reading table per
reel with one row per observation (value, basis, evidence times), plus the cluster decision.

### R1. Cluster the reels before reading them together
- Compare the reels on the uploader account (study file), frame size (`w`,`h`), `face.share`, recurring
  `text.chrome` items (the same text at the same x,y), recurring `text.list` events (the same y ±3 and a similar
  `line_h` at a similar `t0`), and the layout on the sheet.
- A reel joins a cluster when it shares **two or more devices** with it. A reel that shares none becomes a separate
  variant or is excluded, and the reason is written down.
  - `itstundeanthony-C1-K1UfM_eB` (360x640, typed code under language labels, no "Fact or Hype" items) is excluded.
  - `kamchai-DeQr_7OKgcZ` (`face.share` 0, a phone filming a monitor under a fixed 4-row title) is excluded. The
    study file shows it was posted by a different account handle from the other two.

### R2. Rhythm: cuts, read from the measurement
**R2.1 Read the measured fields.** Read `cuts.n`, `cuts.per_min`, `cuts.shot_cuts_per_min`, `cuts.shot_median`,
`cuts.shot_p90` (since v2 both are measured between shot cuts) and `cuts.first`. Derive
`insert_per_min = len(insert_changes) / seconds × 60` and the **shares** `shot = len(shot_cuts)/n` and
`insert = len(insert_changes)/n`. These shares replace the looked cut-kind shares of version 1.
- A **shot cut** means the speaker's shot itself changes: a jump cut, a punch-in, another take, a layout switch that
  moves the face, or a cut to or from full-frame footage. It sets the `takes` boundaries, `zoom.snaps` and layout
  switches.
- An **insert change** means something changes elsewhere while the face box stays put: a B-roll swap inside a split,
  new content in a panel, or an own graphic appearing. It sets the `broll` / panel clips and the graphic onsets.
Keep the median and the p90, not just the rate. Edit rhythm is a distribution, and editors use its long tail on
purpose [S1].

**R2.2 Split the hook from the body.** Find the **hook end**, the first shot cut that changes the layout or opens the
first section (for example the cut out of an inset or the title card). Then derive the **body** values over
`[hook_end, seconds]`: `body_shot_per_min`, `body_shot_median` (shot lengths from the hook end, the last shot ending at
`seconds`), and the body shares. Hooks often run a different rhythm from the body, and one reel-wide number hides that.

**R2.3 Audit the measurement on the sheet (known failure modes).**
| failure | how it shows | seen in | what to do |
|---|---|---|---|
| **a second face on screen** (an inset clip of another person, a picture-in-picture, a call) | the inset's own cuts and stickers are labelled `shot_cuts` while the speaker stands still | `De1zlGniBQp` 0.10–6.97 s (six "shot cuts" while stickers pop on the inset), `DfIM7fyIZXI` 2.93 s | relabel them as insert changes for that span (`looked`) and say so |
| **own graphics count as insert changes** | an insert change within ~1.5 s of an own-graphic `t0` with no B-roll change on the sheet | `DeUOm5syXua` 5.30 (icons), 29.70 (yellow label), 32.43 (punch) | count it as a graphic onset, not a footage cut |
| **a cut to full-frame footage labelled as an insert** | an insert change where the sheet shows the face leaving the frame | `Detm2VPS1Mp` 7.67 s | count it as a layout shot cut |
| **a non-cut** | a punch-in zoom or a card appearing, about 1 detection in 10 (FIELDS.md) | | drop it if the sheet shows no cut |
Write any corrected counts as `derived` and keep the raw measured values next to them.

**R2.4 Name the shot cuts (looked).** The measurement says that the speaker's shot changed, not why. On the sheet,
split the shot cuts into **speaker** (same layout, the pose or framing jumps), **layout** (split ↔ full speaker ↔
full-frame footage) and **cutaway** (a cut between two full-frame footage shots). Shares of shot cuts, marked `looked`.

**R2.5 Coincident cuts.** When a shot cut and a content change in a panel or split land on the same frame, the editor
cut both layers together, so one take boundary brings one new clip. Record it, because it is a lever rule. In the
Fact-or-Hype body, every new screen-recording clip arrives with a jump cut of the speaker. Viewers following the content
miss many within-scene cuts [S19], so a jump cut that lands with new content is a cheap way to tighten the voice.

`cuts.first` describes the hook only if it is a cut of the speaker's shot. If it is an insert change or falls inside a
second-face inset, use the hook end instead.

### R3. Text: split the creator's own graphics from text in the footage
`text.share_of_time` and `text.zones` count every word Vision sees, including screens and app UIs. Sort every
`text.list` event into **own graphic** or **footage text** before using it:

| signal (from the event) | own graphic | footage text |
|---|---|---|
| `rows` | 1–3 | often 5–60 |
| `line_h` | ≥ 1.8 % (captions), ≥ 3.5 % (titles, punch words) | < 1.2 % |
| `letters` | near-white `#F8F8F8`, near-black `#080808`, or one saturated accent (`#F8E808`, `#F8E838`) | many greys `#383838`…`#C8C8C8` |
| `plate` | none, or one flat colour (`#FEFEFE` pill, `#FAF441` label) | many near-identical UI shades |
| position | repeats at the same x,y across reels | drifts with the screen |

A fixed position alone is not enough. A background object (a book spine, a lamp) also sits still. kg03's "Tlia" at
x 60, y 20.5, read on and off for 90 s in dark letters, is the set, not a graphic. Then give each own-graphic event a
**role** and record its `y`, `line_h`, `rows`, `plate`, `letters`, duration and anchor time. The roles are:
- **caption**: speech-synced phrases at a fixed y, about 1–2 s each;
- **punch**: 1–2 rows, `line_h` ≥ 5 %, on a spoken keyword (signalling [S3]);
- **title**: `t0` = 0, held 2–9 s;
- **label**: a short line on a plate;
- **bar**: in `text.chrome`, or lasting to the end;
- **cta**: in the last ~4 s, or repeated (a comment keyword, a handle);
- **cutaway-text**: centred text on full-frame footage.
Vision words are approximate, so match roles to speech by timing.

### R4. Read zones against the face, then in absolute y
`text.zones` is relative to the face. When the speaker sits in the lower half (`face.top` > 40), a caption on a seam at
y≈50 counts as `above`. Always record each role's absolute `y`. Scoring uses absolute y, and zones only check the face.

### R5. Face and layout
- `face.share` < 0.95 → full-frame footage takes about `1 − face.share` of the time.
- `face.top` > 40, or `face.cx` > 58 or < 42, points to a split or a side inset. Confirm it on the sheet.
- Record the **layout of each sampled shot** from the sheet: `full-speaker`, `split`, `panel`, `inset` or
  `full-cutaway`. Weight each shot by its length to get the share of time (`looked`). Since v2, the layout switches are
  the shot cuts named `layout` in R2.4, so a layout block's length comes from measured times.
- **If the sheet stops before the reel ends** (it shows up to 24 frames, so `Detm2VPS1Mp` stops at 29.67 s of 52.2 s),
  compute the shares only over the covered span and say so.

### R6. Audio
`audio.pauses_per_min` and `audio.longest_pause` show how tightly the voice is cut, which sets the `takes` padding and
`hold`. Do **not** save `audio.lufs` as a style. Platforms normalise loudness on delivery [S11].

### R7. How to look at a contact sheet
Write one line per frame: the layout, where the head is, each own graphic with its style, and any sticker or logo.
Look for: (1) **type style**: weight, italic, case, outline, plate shape and which word takes the accent; (2) **plates
Vision misses**, such as translucent strips; (3) **recurring treatments**; (4) **framing**: shot scale, setting, and
whether the pose jumps between frames (this is how you name shot cuts, R2.4); (5) **the last frame**; (6) **frames
whose label disagrees with the picture** (R2.3). You cannot see entry or exit motion, sound, transitions, per-word
effects, or anything shorter than one shot. Mark these `unknown`.

---

## 2. SAVE (spec-writer agent)

Input: the reader's tables for one cluster. Output: one JSON file valid against `format.schema.json`, plus a
one-paragraph reading.

### S1. Every numeric field is a range, with its source and lever
Save `observed: [min, max]` across member reels and an **accept** band:
`accept = [min − w, max + w]` with `w = max(0.15 × |bound|, floor)` for magnitudes (times, durations, rates, sizes).
Positions and shares get the floor only. The floors are **0.5 s** for text times (2 fps sampling), **0.25 s** for shot
lengths, **3 %** for positions, **0.5 %** for `line_h`, **0.05** for shares, **3** for per-minute rates and **1** for
`rows`. Clamp shares to [0, 1], rows to ≥ 1 and times to ≥ 0. With **n = 1** use ±25 % and `confidence: "low"`. Each
field stores `n`, `basis`, `source` and `lever`.

### S2. What to save
- **rhythm**: the measured `per_min`, `shot_per_min`, `insert_per_min`, `shot_median`, `shot_p90` and `first`; the
  measured `cut_shares` (`shot`, `insert`); the derived **body** values (`body_shot_per_min`, `body_shot_median`); the
  looked `shot_kinds` (`speaker`, `layout`, `cutaway`); and `coincident` (true when shot cuts and panel changes land
  together). Each one sets `takes`, `zoom.snaps`, `broll` switches and clips.
- **text roles** (R3): one entry per role, with `y`, `line_h`, `rows`, duration, `plate`, `letters`, `gap` and its
  lever. For Latin type, font size ≈ `line_h% × 19.2 × 1.2` px. For Thai use `× 0.8`. Correct both after the first
  render (C5).
- **text totals** from own graphics only (`derived`), with the raw values kept in a note.
- **layout**: the `face.*` fields → `zoom.base`, `zoom.faceAt`, `broll.shift`; layout shares; block length.
- **audio**: `pauses_per_min`, `longest_pause` → `takes` padding, `hold`.
- **devices** (S3) and **structure**: the hook (0 to the hook end), the body, the end, each with its measured times.

### S3. Devices
A device is a recurring treatment with a job. Save `id`, `what`, `when` (an `anchor` of `hook | spoken-cue |
section-change | persistent | end`, its time range and cue), `where`, `seen_in` (k of n with evidence times),
`role` (`signature` if k/n ≥ 2/3, otherwise `optional`), `lever` and `needs` (the material a new clip must have). A
beat whose length is the same in every member reel, such as the Fact-or-Hype question shot of 1.97 s in all three, is
a device with a measured `duration`.

### S4. What not to save
Topic words, product names, `audio.lufs`, raw footage-text shares as style, and anything `unknown`. Save the
*function* ("the claim's own page shown before the test"), not the content.

---

## 3. FIT (fit-checker agent)

Input: a saved format and the new raw clip (transcript words with times, `face.json`, duration, pauses, and the
material the user has). Output: a fit table, then a reel.json fragment.

### F1. Decide per field and per device: **keep · adapt · drop · ask**
| test | what you compare | fails → |
|---|---|---|
| **material** | the device's `needs` vs what the user has | drop or ask. Never fake a screen recording, a product, a result or an offer. Stock footage illustrates only |
| **spoken cue** | the cue in the transcript (a number, a name, a "not X", a question) | drop that instance |
| **geometry** | the device's y-range vs the clip's face box after `zoom.base`. Faces draw the first fixations [S2], so graphics never cover the face | adapt `y`, `place`, `impact.top`, `zoom.faceAt`, `broll.shift` |
| **density** | per-minute rates × clip length | keep rates, not counts; flag a clip outside `length.accept` |
| **pace** | `body_shot_per_min.accept` vs the speech | reach the shot-cut rate with take boundaries at sentence starts and `zoom.snaps`; reach the insert rate with B-roll or panel clip changes. **Never drop words to hit a rate** |
| **coincidence** | the format's `coincident` flag | if true, start each panel/B-roll clip on a take boundary (`beats[].at` = the take's `a`) |
| **readability** | duration vs words (F2) | split events, trim on-screen words, lengthen `to` |
| **language** | Thai or English (F3) | adapt sizes and line breaks |
| **platform** | safe area: `platform`, `layout.capBottom`, no card below y 1470 | move up |

### F2. Reading-time floor
Every own-graphic event stays up at least **max(1.0 s, 0.3 s per word)**. Netflix's minimum is 5/6 s [S7]. For Thai,
allow at most **17 characters per second** and **35 characters per line**, not counting tone marks and upper or lower
vowels, with two lines at most and one preferred [S6]. For English, keep captions under 3 words/s. TikTok's 5–10
words/s [S9] is an upper bound for an overlay, not a target. Captions stay on by default: they improved comprehension
without a measured rise in load [S4], and WCAG 1.2.2 asks for them [S12]. The exception is a format that puts its own
text where captions would go. Short keywords help; full redundant text competes with the picture [S3].

### F3. Thai specifics
Break lines only at phrase boundaries, because inserted spaces help Thai readers [S5]. Use `|` for rows. Split a row
that would pass ~900 px; never go below the builder's 64 px warning. Use Kanit or Kanit Medium for display rows, and
Prompt or Anuphan for captions.

### F4. Output
A table with `format range → clip value → decision → lever = value → reason`, then the reel.json fragment. Mark every
`drop` and `ask`.

---

## 4. SCORE (critic agent)

Input: the format, the fit table, and the render's spec JSON + contact sheet. Output: gates, a score card and at
most three fixes.

### C1. Gates (every format)
A reel that fails any gate is not shippable:
1. **Face covered**: own graphics in `zone` `face` beyond the format's own share + 0.05, confirmed on the sheet [S2].
2. **Unreadable**: an event shorter than max(1.0 s, 0.3 s/word); Thai > 17 cps or > 35 chars/line [S6][S7].
3. **Out of the safe area**: an own card or caption with `y` > 76.5 % (1470 px) or under the top chrome.
4. **Two caption layers**: two speech-synced text roles on screen at once.
5. **Low contrast**: small text (`line_h` < 3 %) with no plate and no outline over busy footage [S12].
6. **Flashing**: more than 3 flashes in one second [S12].

### C2. Field scores
Inside `accept` scores 1. Outside scores `max(0, 1 − d / width)`. Use the same derived definitions as the format
(own graphics only, body after the hook end, the same R2.3 corrections). Weights:

| group | fields | weight |
|---|---|---|
| devices | each kept signature device at its anchor and y-band on the sheet (1/0) | 0.40 |
| rhythm | `body_shot_per_min`, `insert_per_min`, `shot_median`, `shot_p90`, hook end, `cut_shares` | 0.25 |
| text | role `y`, `line_h`, duration, `gap`; text totals; `first_seen` | 0.20 |
| layout & voice | `face.*`, layout shares, `pauses_per_min`, `longest_pause` | 0.15 |

`score = Σ weight × mean(group)`. A score ≥ 0.85 is *on format*, 0.70–0.85 is *close* and < 0.70 is *off format*.

### C3. Hook check
TikTok asks for the proposition within 3 s and the hook within 6 s [S9]. YouTube's retention report shows where viewers
leave [S10], and Shorts analytics show how many viewers swiped past [S16]. The critic checks that the hook devices
show in the first 3 s, that the first own text appears at `first_seen`, and that the hook ends inside
`structure.hook.seconds.accept`. It reports conformance, never predicted retention.

### C4. Fixes
Give the three largest weighted losses as `lever = value`. Never suggest something the fit dropped.

### C5. Calibration on TadClip's own reels
Run the critic on `kg01k`, `kg03` and `clinic-after` first. With measurer v2, `kg01k` scored against kamchai's split
format gives a more precise diagnosis than v1. Its layout matches: top-half B-roll, a seam phrase with a yellow
keyword, and the speaker low (`face.top` 62.3). Its **insert rate is on format**: 10 insert changes in 62.4 s is
9.6/min, inside accept [3.6, 15.6]. Its **shot-cut rate is not**: 18.3/min against accept [25.4, 38.3] scores 0.45.
`shot_median` is 2.72 s against [1.13, 1.82], and `text.gap_median` is 2.5 s against [1.0, 2.0]. So the B-roll changes
often enough, but the speaker's shot is cut about half as often as kamchai's. The critic should say: "close; add take
boundaries or `zoom.snaps` at sentence starts inside split blocks (not more B-roll), and put own text on more
sentence starts". If the critic disagrees with what the sheet plainly shows, fix the critic first.

---

## Appendix A. Field → lever map
| measured | lever |
|---|---|
| `cuts.shot_cuts_per_min`, body shot rate, `shot_median`, `shot_p90` | `takes` boundaries, `zoom.snaps`, `zoom.pushes`, layout switches |
| `insert_changes` (per min) | `broll` `clips` inside a split, panel clip changes, graphic onsets |
| `coincident` | panel/B-roll beat `at` = take start |
| hook end | the first layout switch or the end of the title/inset beat |
| `audio.pauses_per_min`, `longest_pause` | `takes` b-padding, `hold` |
| `face.top`, `face.cx`, `face.height` | `zoom.base`, `zoom.faceAt`, `zoom.origin`, `broll.shift` |
| caption role | `captions.style`, `captions.y`/`splitY`, `size`, `strip`, `onlyInSplits` |
| punch / title / label roles | `impact` (`look`, `place`, `y`, `size`, `impact.color`, `impact.plate`), `textfx`, `title` |
| bar | `verdict`, `chrome` |
| inset / panel / split | `broll mode: panel` (`box`, `frame`), `polaroid`, `broll mode: split` (`h`, `shift`) |
| CTA | `cta`, `linecta`, `endcard` |

## Appendix B. Known blind spots
- Motion, sound, music and transitions: `unknown`.
- Vision text is approximate for stylised Thai and handwriting.
- One frame per shot. The sheet holds at most 24 frames, so long reels lose their ends.
- Measurer v2's failure modes (R2.3): second faces, graphic onsets, cuts to full-frame footage.
- Two or three reels bound a format loosely. Re-run R1 and S1 when new reels arrive.
