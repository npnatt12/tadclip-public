# Clone: copy a creator's style, or a viral video's structure

The two routes that start from someone else's video. Both end in the normal pipeline, on ClubGig. A real person is
always on camera: nothing here generates a presenter.

The reading is TadClip's own format engine (`docs/format-engine/`): every reel is **measured** first
(`scripts/format_spec.py`: cuts of the speaker vs inserts, text events with place, size and colours, face, pauses), and
an agent reads the numbers with the contact sheets, following the briefs in `docs/format-engine/method/`. Numbers
decide rhythm, size and place; the agent decides what recurs and why it works.

**Never copied:** the creator's face, words, logos, music, footage or graphics files. Copy the system (rhythm,
placement, type treatment, structure), not the content. Nothing on screen says anything the speaker did not say.

## Route A: "ตัดต่อคลิปนี้ให้เป็นสไตล์ @creator"

1. **Saved already?** If `styles/creator-<handle>.json` exists, skip to step 6.
2. **Find the reels.** A bare handle means Instagram: open `instagram.com/<handle>/reels/` with the Chrome tools (the
   user's own logged-in browser), read the display name, and take links to the 3-5 most-viewed recent reels where the
   creator talks to camera. Another platform only if the user says so (`--youtube`); the same handle there can be
   someone else. `python3 $S/scripts/creator_study.py <links> --out $P/study`, then tell the user whose reels you studied.
3. **Measure each:** `python3 $S/scripts/format_spec.py $P/study/<id>.mp4 --out $P/study/<id>.spec.json --sheet $P/study/<id>.sheet.jpg`.
4. **Read and save** with `docs/format-engine/method/briefs/reader.md` then `spec-writer.md` (METHOD.md parts 1-2):
   cluster the reels, read the rhythm (`cuts.shot_cuts_per_min`, not raw cuts), text roles, layout and devices, and
   save `styles/creator-<handle>.format.json` (valid against `method/format.schema.json`: ranges, devices, levers).
5. **Write the overlay** `styles/creator-<handle>.json` from the format's levers: only the keys that differ from ClubGig,
   plus `_about` (one paragraph in plain words) and `_source` (study folder, date, reels). Add a row to
   `references/styles.md`. The overlay keys: `impact` (plate colours, `look`, `maxGap`), `broll` (`mode: split|panel`,
   `panel`), `captions` (style, y, size, `onlyInSplits`, `splitY`, `strip`), `verdict`, `zoom` (`base`, `faceAt`),
   `sfxProfile`, `music`, `look` (never grades the face unless asked).
6. **Fit** with `briefs/fit-checker.md` (METHOD part 3) against THIS clip's transcript and face track: keep / adapt /
   drop / ask per field and device. A device the clip has nothing for (a verdict on advice, a panel with no screen
   recording) is dropped and said in one line before editing: "This is a verdict format and your clip is advice, so
   I'm keeping his look and dropping the checkbox." None of it fits: say so and suggest ClubGig; the user decides.
   Labels come from this clip's topic, never a placeholder or the creator's series name.
7. **Edit:** the normal ClubGig pipeline with `style: "creator-<handle>"`; plan the beats in the format's structure and
   re-budget `recipes/clubgig/README.md` to its pace. Say what the builder can't do instead of faking it.
8. **Score before showing:** measure the preview (`format_spec.py`) and run
   `python3 $S/scripts/format_score.py styles/creator-<handle>.format.json <preview spec>`; then `briefs/critic.md`
   (METHOD part 4: gates first, then at most three fixes). Fix and re-render once if a gate fails or the mean is under
   0.70. Show one reference frame next to one frame of the result, then the preview.

## Route B: a viral link with no raw clip

1. **Fetch, measure and tear down:** `creator_study.py <link> --out $P/study`, `format_spec.py` on it, then the video
   teardown (`recipes/rea/README.md`). Given a handle, pick the most-viewed reel where the creator talks to camera: the
   top number is often a collab or a clip with no speech.
2. **Write `$P/clone-brief.md` and stop for the user's OK:** why it works, in timecodes (from the teardown); a beat
   table (what each beat does for the viewer, not its seconds); a Thai shooting script in the speaker's own voice,
   saying only what is true for them, never the original's lines; a table tracing each claim to something the speaker
   has said, marking anything new for them to check; and filming notes (chest-up, with room on the torso for popups;
   say each line twice).
3. **They film it.** Then the normal pipeline in ClubGig; the brief's beat table guides the plan, and step 8 of route A
   scores the result against the teardown's format.

AI-generated B-roll is not part of TadClip: stock B-roll as ClubGig does.
