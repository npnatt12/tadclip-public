# Annotating reels (for an editor who hasn't seen the format engine)

Watch each reel in `reels/` on a phone or a laptop, as many times as you like, with a stopwatch or the player's time.
Fill one row of `annotations.csv` per reel. Don't look at anyone else's answers. 2-3 editors annotate the same reels:
how much you agree with each other is the best any machine can do.

| column | what to write |
|---|---|
| `reel` | the file name |
| `editor` | your initials |
| `speaker_cuts` | how many times the speaker's own shot jumps (a jump cut, a new angle, a zoom that snaps). Not B-roll, not panels |
| `inserts` | how many times a picture, clip, screen recording or panel appears over or instead of the speaker |
| `text_where` | where on-screen words sit most of the time: `above` the face, on the `face`, on the `chest` (just under the chin), `lower`, or `none` |
| `text_plate` | `yes` if the words sit on a coloured block or card most of the time, else `no` |
| `captions_word_by_word` | `yes` if the words follow the speech a few words at a time, `no` if they are short headlines |
| `first_text_s` | when the first words appear (seconds) |
| `music` | `yes` / `no` |
| `devices` | the recurring treatments you'd copy, in your words (e.g. "question card on top, ticks a box at the end") |
