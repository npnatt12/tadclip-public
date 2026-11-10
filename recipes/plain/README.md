# Plain ("เริ่มจากศูนย์", "from scratch")

The best take of each line, the pauses out, big word-timed captions off the face, and nothing else: no cards, B-roll,
sound effects, music or logo unless their words after "ผู้ใช้อยากได้:" ask for them (then add exactly those, with the
tools of the style that does it best: `transitions`, `broll`, `music` in references/reel-json.md). Their own brand
(~/TadClip/brand/) is applied by build.mjs: font and colour on the captions, their logo on an end card.

Built 11-09 after the evening test: without a recipe the helper wrote its own Thai word splitter and caption chunker
mid-run (12 turns, $5.15, 54 min against the ClubGig run's 6 turns, $2.17, 30 min). Everything below already exists.

Progress lines (`[n/7] ไทย | English` into `$P/build/progress.log`, the app shows them):

1. `[1/7] เตรียมวิดีโอ | prep, ~3 min`: `bash $S/scripts/prep.sh <clip> $P` (an iPhone HDR clip is tone-mapped: ~2.5 min for 5 min)
2. `[2/7] หาหน้าและถอดเสียง | face + speech islands + transcript, ~5 min`, one after the other, all in the foreground:
   `python3 $S/scripts/face_track.py $P/assets/talk.mp4 --out $P/build/face.json`;
   `ffmpeg -v error -y -i <clip> -vn -ac 1 -b:a 96k $P/build/voice-raw.mp3` (the ORIGINAL clip's sound: same timeline as
   talk.mp4, measured 0.0 ms; prep's loudness normalisation makes breaths count as speech: 397 s vs 221 s, 1.9 % vs 1.5 % errors);
   `python3 $S/recipes/clubgig/islands.py $P/build/voice-raw.mp3 $P/build/vad.json`;
   `~/.venvs/mlxw/bin/python $S/scripts/islands_tx.py $P/build/voice-raw.mp3 --vad $P/build/vad.json --lang th --out $P/build/islands.json`.
   No whole-file `transcribe.py` (it loops on long Thai clips), nothing in the background. Measured on a fresh account
   (11-09, 4:50 iPhone clip, M3): prep 154 s, face 100 s, transcript 221 s: 7.9 min with step 1.
3. `[3/7] เลือกเทค | choose takes, ~3 min`: read islands.json; pick the best complete take of each line (references/take-selection.md),
   correct whisper's Thai against the meaning (names as profile.json spells them). Copy `$S/recipes/clubgig/cut.py` to
   `$P/build/cut.py`, replace TAKES with `(a, b, "verbatim corrected text")`, run `~/.venvs/mlxw/bin/python -I build/cut.py`
   -> build/words.th.json (caption chunks timed to the voice) + build/takes.json. Don't write your own splitter.
4. `[4/7] ประกอบคลิป | reel.json + build, ~2 min`:
   `{"title": "...", "style": "clean", "source": "assets/talk.mp4", "words": "build/words.th.json", "takes": <takes.json>,
   "captions": {"style": "clean"}, "beats": []}` plus only what their words ask for. No `captions.size` or `group`: Thai
   captions default to 2x (~128 px) and one phrase per screen, placed off the face; a smaller size needs
   `captions.asked` with their words. `node $S/scripts/build.mjs $P`: 0 warnings.
5. `[5/7] ตรวจภาพ | approval sheet, ~2 min`: `python3 $S/scripts/approval_sheet.py $P` and LOOK: captions readable, none on the
   mouth, nothing past the edge.
6. `[6/7] เรนเดอร์ตัวอย่าง | preview, ~5 min`: `python3 $S/scripts/finals.py preview $P --out $P/finals --style "Plain" --code <CODE> --title "..."`,
   one foreground call (timeout 600000).
7. `[7/7] ส่งคลิปตัวอย่าง | hand over, ~1 min`: the preview + a cover jpg (the first frame with the face clear, from the approval
   sheet, not frame 0) next to the clip; the summary as the app asks (plain Thai, what to check before posting last).
