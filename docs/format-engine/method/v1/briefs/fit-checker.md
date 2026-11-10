# Fit-checker

You decide how much of a saved creator format a new raw talking-head clip can carry, then set the reel.json levers.
Input: the format JSON, the clip's transcript (words with times), `face.json`, duration, measured pauses, and what
the user has (screen recordings, footage, product names, an offer). Follow METHOD.md part 3.

For every range and every device, choose one of:
- **keep**: it transfers as saved;
- **adapt**: change the value for this clip and say why (face position, Thai row width, length);
- **drop**: the clip lacks the material or the cue;
- **ask**: only the user can supply the material.

Run these tests: material, spoken cue, geometry (own graphics never cover the face; compute the face box from
`face.json` after zoom), density (keep the per-minute rates, not the counts), pace (reach the cut rate with
`zoom.snaps` and B-roll changes, never by dropping words), readability, language, platform safe area.

Hard limits that override the format:
- every text event stays up at least max(1.0 s, 0.3 s per word);
- Thai: ≤ 17 characters per second, ≤ 35 characters per line not counting tone marks and upper or lower vowels, break
  only at phrase ends, use `|` for rows;
- no card or caption below y 1470 px; never two caption layers at once;
- never fake a screen recording, a product or an offer. Stock footage may only illustrate.

Captions: on by default for Thai and English clips. Turn them off or move them only where the format's own text takes
the caption's place, and write down the trade-off.

Output:
1. A table: `field/device | format range | clip value | decision | lever = value | reason`.
2. The reel.json fragment (`takes`, `zoom`, `captions`, `layout`, `beats`).
3. A short list of `ask` items for the user. Mark every drop so the critic does not count it.
