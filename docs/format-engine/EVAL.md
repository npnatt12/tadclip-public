# Format engine: evaluation (2026-11-10)

What is scored here, and by what: the measurer against ground truth that no one has to judge (TadClip's own reels,
whose build file records every cut); the method's text against Hypit's (word overlap, pass line fixed beforehand); the
current Hypit-based route's saved formats against the measurements. What needs people (independent editors, a blind
A/B, real audiences) is set up but not yet run: see the end.

## 1. The measurer against ground truth (TadClip's own reels)

`tools/format-eval/cuts_truth.py`: each built reel's `index.html` records when every take (jump cut) and every insert
starts. Tolerance 0.2 s.

| reel | jump cuts | found | missed (why) | detections matching a real visual change | timing error (median) |
|---|---|---|---|---|---|
| clinic re-render (88 s) | 15 | 15 | none | 30 / 33 (91 %) | 0.00 s |
| KG01K, Kamchai format (62 s) | 15 | 12 | 1 under a full-screen insert (invisible), 2 with the speaker shrunk into a split screen | 28 / 29 (97 %) | 0.03 s |
| KG03, ClubGig (93 s) | 14 | 13 | 1 under a full-screen insert (invisible) | 28 / 32 (88 %) | 0.00 s |
| **all** | **44** | **40** | **visible cuts found: 40 / 42 (95 %)** | **86 / 94 (91 %)** | **0.00 s** |

"Real visual change" = a take, an insert, a swipe, a punch-in or push, a card or end card appearing (from the build).
Split by kind: of the 40 jump cuts found, 36 were classed as cuts of the speaker's shot (the face box itself changes),
4 as insert changes (all in KG03 and KG01K, during split screens).

## 2. The current Hypit-based route, checked against the measurements

The two creator formats saved by the current route (`styles/creator-*.json`, 2026-11-05), each claim that can be
measured, against `format_spec.py` on the same reels (`specs2`, the speaker-shot cut classifier):

| creator | the saved format says | measured | |
|---|---|---|---|
| itstundeanthony | "About 3 cuts a minute" | 11.7-20.0 cuts of the speaker's shot a minute (4 reels; checked by eye: the face jumps at 9 of 10 cuts in DdWmIHTC322) | **wrong**: the old study's measurement had failed (`seconds: 0`, `cuts: 3`) and the agent used it |
| itstundeanthony | speaker high in the frame | face top 23-28 %, bottom 40-50 % | right |
| itstundeanthony | checkbox bar on the chest, framed panels low | text time: chest 27-76 %, lower 3-67 % | right |
| kamchai | "a new shot every 2-3 s" | median shot 1.4-1.6 s (p90 2.9-3.4 s) on the two talking reels | **too slow by ~40 %** |
| kamchai | speaker in the bottom half | face 45-71 % of the height | right |
| kamchai | headline on the seam, above the speaker | text time above the face 74-76 % | right |

So the current route reads layout well by eye and gets rhythm wrong when its numbers are wrong. Measured numbers fix
exactly the part a model can't see on a contact sheet.

## 3. The method's text against Hypit's

`tools/format-eval/overlap.py <method> vendor/hypit` (8-word sequences; pass: <= 1 % and no shared run of 15+ words,
fixed before the method was written). Sanity: Hypit's own `transformations.md` against Hypit scores 100 % (FAIL), our
own `recipes/clone/README.md` (which paraphrases Hypit's ideas in our words) scores 0 %: the check catches copying and
close paraphrase, not ideas, which is why the room is sealed (PROVENANCE.md).

**Result: PASS, both sessions.** All of `method/` as it stands after session 2 (the revised METHOD.md, the schema,
the briefs, the two formats and their readings, the teardown method `rea/` and the competitor analysis
`competitors/` with their templates, briefs and examples, plus v1 kept in `method/v1/`: 41,631 eight-word sequences)
against all of Hypit's text (9,855 lines; `vendor/hypit/` as it is on `main`, since this branch removes it):
**0 shared sequences (0.00 %), longest shared run 0 words** (re-run 2026-11-10). Session 1 alone: 13,587 sequences,
0.00 %.

The room's access log (kept private) has 177 calls across both sessions (74 + 103) and **1 refused**: in
session 2 the room tried to read its own saved web-fetch result, which Claude Code keeps outside the room; the guard
refused the path and the session fetched the page again. The 31 fetched pages are papers, standards and platform help
(session 1: Netflix's Thai and general timed-text guides, WCAG 2.2, EBU R 128, TikTok's and YouTube's creator help,
Psychological Science, JoSTrans, Western Sydney University, BBC; session 2 adds copyright law (US and Thai), platform originality and analytics pages, and attention research for
the teardown and the competitor analysis: `method/SOURCES.md`).

## 4. Saved formats: clean-room method vs current route

Both clean-room formats (session 2's revision) are valid against the room's own schema (`jsonschema`, draft 2020-12). Compared with the
current route's saved formats for the same creators:

| | current route (`styles/creator-*.json`) | clean-room method (`method/formats/`) |
|---|---|---|
| size | one `_about` sentence + 6-8 builder settings | 216-261 lines: every field a range with its source and its builder lever |
| rhythm | itstundeanthony "about 3 cuts a minute" (wrong); kamchai "every 2-3 s" (slow) | itstundeanthony 13.3-20.7 cuts/min (accept 10.3-23.8); kamchai median shot 1.2-1.4 s (accept 0.95-1.65): both match the measurements |
| devices | named in prose | 6 and 8 devices, each with where, when (anchor), k of n reels with evidence times, signature/optional, the lever and what material a new clip needs |
| reels that don't fit | used | excluded with the reason (itstundeanthony C1-K1UfM_eB, an older series; kamchai DeQr_7OKgcZ, a POV series) |
| unknowns | not said | listed (animation, sound, music, transitions) |
| fit and score | none | a fit table per field and device (keep / adapt / drop / ask); a critic score with gates (face, readability, safe area, contrast, flashing) and three fixes |

**Erratum, resolved in session 2.** Session 1's METHOD R2 and itstundeanthony reading said most of the Fact-or-Hype
cuts after the hook are panel changes, judged from the contact sheets. Version 2 of `format_spec.py` measured that the
speaker's face jumps at 9 of 10 cuts in DdWmIHTC322. Session 2 got the v2 measurements and revised the method to read
rhythm from `cuts.shot_cuts` vs `insert_changes` (`method/CHANGES.md`); session 1's text is kept in `method/v1/`.

**Calibration** (`format_score.py`, the revised Kamchai format against KG01K, TadClip's own reel made with the old
route's Kamchai style): 8 of 17 measured fields in range, mean 0.76. Layout and text land (face height, centre, share;
text size, rows, first text at 0 s); rhythm misses: shot median 2.72 s vs 1.13-1.82, speaker cuts 18.3/min vs
25.4-38.3. That's the reel being built from the old saved format's "every 2-3 s" (section 2): the score catches the
exact error the measurements found, before anyone has to watch it.

## 5. Teardown and competitor reports (the script's part)

`video_rea.py` measures each reel and fills the report templates; the agent writes the rest. Run on the saved test
reels (2026-11-10): `competitors` with itstundeanthony (4 reels), kamchai (3) and TadClip's own (KG01K, KG03), 9
teardowns. Every number the script can produce is filled: in each teardown the numbers table, the cut list (each cut
labelled speaker or insert), every text event with place, size, rows and colours, and the first 10 seconds second by
second; in `compare.md` the accounts table and 13 measured rows of the comparison, one column per account with the
owner last. What needs eyes is handed over as `[agent: hint]` (hook end and pattern, layout, caption policy, roles).
The hook end is provisional (3 s) until the agent sets it; body numbers count from it.

`video_rea.py --check` fails if a template loses a row the script expands. The first version of the script missed
exactly this: session 2's templates replaced the table slot, so the comparison table was silently dropped.

What the comparison already says, before any reading: Kamchai's body runs 30.8 speaker cuts/min (median of 3) against
our KG01K/KG03 at 16.8 and itstundeanthony at 13.9; our reels carry 7 insert changes/min, Kamchai 6.6, itstundeanthony
1.1. No views were available (Instagram didn't return them to `creator_study.py`), so it is descriptive.

## 6. Not run yet (needs people)

- **Independent editors:** `tools/format-eval/ANNOTATE.md` + `annotations.template.csv`; 2-3 editors annotate the
  same 20-30 reels; `agree.py` gives editor-vs-editor agreement (the ceiling) and engine-vs-editors per field.
  The 10 reels here are a start; 10-20 more from other creators (links pasted by the owner) are needed.
- **Blind A/B:** the same raw take edited with the current route's format and with the clean-room format; viewers who
  don't know which is which pick the one closer to the creator.
- **Real audiences:** retention and watch time in Instagram Insights for posted reels, over weeks.
- **Legal:** the memo's questions to Hypit.AI, GSAP and a lawyer.
