# Clone: copy a creator's style, or a viral video's structure

The two routes that start from someone else's video. Both end in the normal pipeline, on ClubGig. A real person is
always on camera: nothing here generates a presenter.

The judgment comes from Hypit, copied unmodified in `vendor/hypit/` (see its SOURCE.md). Read these two before either route:
- `vendor/hypit/references/creation/reference-video.md`: how to read a video (why it holds attention, what each cut, reveal
  and sound responds to, which systems persist).
- `vendor/hypit/references/creation/transformations.md`: what to keep and what to recreate for a new person or message.

Only that thinking is used. The `hypit` program is not installed, so swap its commands:

| Hypit says | TadClip uses |
|---|---|
| `hypit download` | `scripts/creator_study.py` (latest yt-dlp through uvx) |
| `hypit transcribe` | `whisper`, or the Thai pipeline in `recipes/clubgig/README.md` |
| Brief / Treatment files | the style's `_about`, or `$P/clone-brief.md` |
| SVML, SVS, SVRun, Timeline, Components | `reel.json` beats (`references/reel-json.md`) |
| generated image, video, voice | stock B-roll as ClubGig does. AI B-roll needs the `hypit` program, an account and paid credits: ask first |

**Never copied:** the creator's face, words, logos, music or graphics files. Copy the system (rhythm, placement, type
treatment, sound level), not the content. Nothing on screen says anything the speaker did not say.

## Does the format fit the clip?

Check this before planning beats, on both routes. Copying a style correctly can still make no sense: a verdict bar on a
relationship talk has nothing to judge (the owner on the KG03 test, 2026-11-05: the style landed, the context didn't). Read the
transcript and answer: what does each device need from the content (a claim to judge, a screen to show, a number to reveal),
and does this clip have it?

- All of it: go ahead.
- Some of it: keep the look, drop the devices that have nothing to work with, and say so in one line before editing.
  "This is a verdict format and your clip is advice, so I'm keeping his look and dropping the checkbox."
- None of it: say so and suggest ClubGig or a better-fitting creator. The user decides.

Any label on a device comes from this clip's topic, never a placeholder and never the creator's series name.

## Route A: "ตัดต่อคลิปนี้ให้เป็นสไตล์ @creator"

1. **Saved already?** If `styles/creator-<handle>.json` exists, skip to step 5.
2. **Find the reels on Instagram first.** A bare handle means Instagram: open `instagram.com/<handle>/reels/` with the Chrome
   tools, read the display name and follower count, and take links to the 3 most-viewed recent reels (plus their biggest
   ever if it matches). Use another platform only if the user says so (`--youtube`); the same handle there can be someone else.
   Then `python3 $S/scripts/creator_study.py <links> --out $P/study` and tell the user whose reels you studied.
3. **Read it** (reference-video.md), at least 3 videos where the creator talks to camera; skip other formats. `sheet.jpg`
   and `frames/` are the evidence; `edit-log.txt` is a draft and may be missing when Gemini is down. `cuts_per_min` is
   a rough floor (subtle jump cuts score low), so confirm it on the sheet. Most big creators run a FORMAT, a repeated
   sequence of devices, not just a look: write the sequence down before touching colours.
4. **Write the overlay** `styles/creator-<handle>.json`, only the keys that differ from ClubGig, and add a row to
   `references/styles.md`. Example: `styles/creator-itstundeanthony.json`.

   ```json
   { "extends": "clubgig", "_about": "...", "_source": { "study": "...", "saved": "YYYY-MM-DD" }, "impact": { ... } }
   ```

   | what you saw | key |
   |---|---|
   | popup colours | `impact.plate`, `impact.plate2`, `impact.color` |
   | popup device | `impact.look`: stair, stack, pill, headline, plate, seoul, paper |
   | footage above, speaker below, most of the reel | `broll` `mode: "split"` beats back to back with `clips`; `headline` on the seam |
   | small captions only over the footage | `captions`: `mini`, `onlyInSplits`, `splitY`, `strip` |
   | screen or clip beside the speaker | `broll` `mode: "panel"`, `broll.panel` |
   | a bar held on screen, a verdict payoff | `verdict` beat |
   | popup density | `impact.maxGap` (and plan fewer popups) |
   | running captions | `captions`: style, y, size, weight, group, stroke |
   | framing | `zoom.base`, `zoom.faceAt` |
   | sound | `sfxProfile`, `music.id`, `music.db` |
   | colour | `look` (never grades the face unless the user asked: `look.asked`) |

   ClubGig keeps the rest: Thai wrapping, Thai fonts only (Kanit, Anuphan, Taviraj), nothing on the face, the brand's real
   logo and LINE CTA. Say what the engine can't do (for example, sliding the speaker aside for a screen panel) instead of
   faking it; propose the closest beat (a straight `polaroid`, a `broll` split) or a new build feature.
5. **Edit:** the normal ClubGig pipeline with `style: "creator-<handle>"`. A style file holds the look; the format lives in the
   beats, so plan them in the creator's sequence and re-budget `recipes/clubgig/README.md` to their pace. Write your own
   words for a series device (the speaker's topic, not the creator's series name).
6. **Show** one reference frame next to one frame of the result, then the preview.

## Route B: a viral link with no raw clip

1. **Fetch and read:** `creator_study.py <link> --out $P/study`, transcribe it, read it as above. Given a handle, pick the
   most-viewed reel where the creator talks to camera: the top number is often a collab or a clip with no speech.
2. **Write `$P/clone-brief.md` and stop for the user's OK:** why it works, in timecodes; a beat table (what each beat does
   for the viewer, not its seconds); a Thai shooting script in the speaker's own voice, saying only what is true for them,
   never the original's lines; a table tracing each claim to something the speaker has said, marking anything new for them
   to check; and filming notes (chest-up, with room on the torso for popups; say each line twice).
3. **They film it.** Then the normal pipeline in ClubGig; the brief's beat table guides the plan.
