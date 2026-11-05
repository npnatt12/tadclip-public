# ClubGig (LOCKED 2026-10-31)

The Thai talking-head house style. the owner approved KG01 ("this is the perfect one") on 2026-10-31: every new Thai reel
in this style must come out like it. Call: **"ClubGig"**, "edit this in ClubGig", "the KG01 look".

## v2 (2026-10-31, the owner on KG02: "the person is larger ... the text should be around the torso")
  wine plates, a third row smaller and stepped right (`"A|{B}|{C}"`; `"A|B"` = white + plate). Never above the head.
  Seoul and paper looks are retired from the default (white italic on a light jacket can't be read): every popup is stair.
  The hook qcard stays over the split stock and ends with the split (`to` = the split's `to`), never over the head.
- **No running captions:** `captions.style: "none"`; the popups carry the words. `"style": "clubgig"` brings them back at y 1380.
- **20 % fewer popups than KG02:** start-to-start <= 9.4 s (`impact.maxGap`); KG02 went 17 -> 14 popups (+ 3 swipe labels).
  The LINE CTA sits on the same torso band and steps aside while a popup plays.

- Preset: `styles/clubgig.json` (look). Worked example: `examples/gallery/clubgig.reel.json` (KG01 beats, verified to
  rebuild the approved composition byte for byte). Read the example before planning a new reel: copy its SHAPE (it predates v2: no seoul/paper looks, no zoom.origin, ~20 % fewer impacts).
- Built on reel.json + `scripts/build.mjs` (no separate builder). Beat docs: `references/reel-json.md` (impact, polaroid,
  linecta, swipe, broll swipe/label/clips, chrome, endcard logo, brand.textShadow).
- Source: Icarus rules (f2df9e7) + Coach Q&A (recipes/coach-qa) + Seoul list + Face RESULT devices.

## What a reel contains (KG01 budget, 89.5 s; scale by length)

| device | KG01 | rule |
|---|---|---|
| hook | `impact look:"qcard"` (148 px, `{...}` line on red) over a **split-screen stock clip** from frame 0 | every hook opens on stock video within 2 s; the qcard is complete at frame 0 |
| chrome | tagline top left + the brand's OFFICIAL logo top right, whole talk | the logo is cut from the brand's own material or `brand_kit.py pull`; never redrawn |
| impacts | v2: ~11 popups + 3 swipe labels per 90 s, `stair` look in Kanit on the torso (roles pick motion + sound only) | speaker's words only; 1.2-4.5 s; <= 9.4 s start to start; no 15 s untreated |
| swiped stock points | 3 full-bleed inserts with the colour swipe in and out + two-tier label (big white + small on maroon) | 2-5 s each, 1-2 clips per point (`clips`), <= 3 a minute; the label is the speaker's words |
| polaroids | 3 (photo, clip, photo) beside the face, handwritten caption | Face RESULT device; never on the face |
| emotional line | v2: a 3-row stair (`"A|{B}|{C}"`) instead of Seoul words | the line the reel turns on |
| flash page | 1 `scene kind:"word"` white, `size: 220` on a connector ("ดังนั้น") | 0.6-0.9 s |
| LINE CTA | `linecta` at ~60 % (the pivot sentence) to the end card | bubble lines + handle are the brand's; captions hide under it |
| punch-ins | 4 impacts with `push: true` (1.16) | the camera moves only with impact text |
| end card | `endcard` with `logo` (dark lockup) on white | ding |
| captions | v2: none (the popups carry the words) | `"style": "clubgig"` turns them back on at y 1380 |
| sound | ~30 hits (~20 a minute) + lo-fi-02 bed at -18 | one cue per impact, whoosh per swipe |

## Pipeline (commands; `S=~/.claude/skills/tadclip`, `P=<project>`)

```bash
export PATH=/opt/homebrew/opt/node@22/bin:$PATH          # HyperFrames 0.8.159 needs Node 22 (finals.py too)
bash $S/scripts/doctor.sh
bash $S/scripts/prep.sh <recording.mov> $P               # iPhone HLG -> Hable SDR automatically (original brightness)
ffmpeg -v error -i $P/assets/talk.mp4 -vn -ac 1 -b:a 96k $P/build/voice.mp3
# the transcript FIRST: Gemini's free tier is 20 requests a day and it resets at 15:00 Bangkok. No transcript, no takes: stop here
python3 $S/scripts/gem_audit.py ask $P/build/voice.mp3 $S/recipes/clubgig/prompt-thai-verbatim.txt --out $P/build/gemini_tx.txt
python3 $S/scripts/face_track.py $P/assets/talk.mp4 --out $P/build/face.json
# Thai words: timing from per-island mlx-whisper, TEXT from Gemini (whole-file whisper drops Thai speech)
python3 $S/recipes/clubgig/islands.py $P/assets/talk.mp4 $P/build/vad.json
~/.venvs/mlxw/bin/python $S/scripts/islands_tx.py $P/build/voice.mp3 --vad $P/build/vad.json --lang th \
    --mlx-model mlx-community/whisper-large-v3-turbo --out $P/build/islands.json
```
1. **Takes** (references/take-selection.md): read gemini_tx.txt against islands.json times; drop the count-in, fillers,
   asides; keep the whole argument + the CTA; cut on real pauses; total speech <= the user's limit minus the 2.2 s outro.
2. **Captions:** copy `recipes/clubgig/cut.py` to `$P/build/cut.py`, write TAKES = (a, b, verbatim Gemini text,
   "?" on questions) from THIS recording's transcript (it refuses the stored KG01 example), run `~/.venvs/mlxw/bin/python -I build/cut.py` -> build/words.th.json + build/takes.json.
3. **Brand:** ask once for the brand's official logo (white wordmark + dark lockup PNGs), the tagline and the LINE
   handle + bubble lines. Ask the user for them once.
4. **Stock:** `python3 $S/scripts/broll_fetch.py search <words> --pexels` (videos) / `photos <words> --dir $P/broll`
   (photos); faceless or distant people first; look at the frames; conform every one:
   `insert_prep.py SRC $P/assets/ins/<name>.mp4 --in S --dur D --ref $P/assets/talk.mp4 --size 1080x1920 --kind stock`
   (`--size 1080x900` for the hook split, `720x864` for a polaroid clip).
5. **reel.json:** start from `examples/gallery/clubgig.reel.json`; replace takes, beats (source seconds, on the spoken
   words), chrome, linecta, endcard logo; keep `style: "clubgig"`, `zoom.origin` on the face, `"broll": {"fullScreenStock": true}`.
6. **Build + look:** `node $S/scripts/build.mjs $P` (0 warnings), `python3 $S/scripts/approval_sheet.py $P` and LOOK at
   every frame (plate visible, impacts above the head, nothing on the face).
7. **Preview:** `python3 $S/scripts/finals.py preview $P --out $P/finals --code <CODE> --style "ClubGig" --title "..."`;
   check the swipe in the RENDER (frames at the cut -0.2/0/+0.1) and send it. WAIT for the user's OK.
8. **Final:** `finals.py render`, `finals.py qa`; then the posting copy at -14 LUFS (the HyperFrames mix lands ~1.5-2.7 dB
   under the voice; never lift the mix): `python3 -c "import sys; sys.path.insert(0,'$S/scripts'); import finals;
   finals.loudnorm('<name>.mp4', '<name> (post).mp4')"`.

## Known traps (all hit on KG01)
- Snapshots (`hf.sh snapshot`) do not decode video: the plate shows black there; judge the plate on approval_sheet / the render.
- A `broll` wrapper is untimed: it must be hidden outside its window (build.mjs does it; a black full-screen box over the
  whole reel meant this broke).
- face.json can hold false detections (a ceiling light): impact / polaroid placement filters them (`faceSpan`).
- Thai line widths come from `library/fonts/thai/metrics.json`; a 2-line impact at 116 px fits ~13 glyphs a line.
- Gemini: `gemini-flash-latest` (free tier) allows only **20 requests a day** (429 RESOURCE_EXHAUSTED after that; it resets
  daily). Do the transcript call first; insert_prep / broll_vision people checks spend the same quota. Pro has no free quota.
- The Pexels key lives in the skill's `.env.local` (`PEXELS_API_KEY`).
