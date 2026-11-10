# Contract 2: video teardown + competitor analysis, and the method's revision (clean room)

Same room, same rules as CONTRACT.md: work only in this folder, write in your own words, cite primary sources you find
yourself in `out2/SOURCES.md`, never look up or paraphrase any existing video-agent product's guides or prompts. The
result ships in a paid product, so everything must be original, and any tool or dataset you recommend must be free for
commercial use (MIT, BSD, Apache-2.0, ISC, CC0, OFL; no GPL/AGPL, no non-commercial licences).

## Inputs (new)
- `inputs/method-v1/`: the method you wrote in the first session (yours: revise it freely).
- `inputs/FIELDS.md`: the measurer is now version 2: `cuts.shot_cuts` (the face box itself changes) vs
  `cuts.insert_changes` (only a panel/card/screen elsewhere changes).
- `inputs/specs2/`: the same 10 reels measured with version 2, with contact sheets.
- `inputs/studies/*.study.json`: where the creator reels came from (URLs, uploader names; views often missing).

## Outputs (`out2/`)
1. **Revise the method** → `out2/method/` (same files as method-v1: METHOD.md, format.schema.json, briefs/, formats/,
   SOURCES.md). Use `shot_cuts` / `insert_changes` instead of classifying cuts by eye where the measurement now does it;
   re-check the two formats against `specs2` and correct anything the new numbers contradict (in particular: in the
   Fact-or-Hype reels the speaker's face itself jumps at most cuts after the hook). Keep a short CHANGES.md.
2. **Video teardown (REA)** → `out2/rea/`: the method an agent follows to reverse-engineer ONE short video for a person
   who wants to learn from it:
   - `REA.md`: what the teardown answers (structure second by second, the hook, each beat's job for the viewer, recurring
     devices, why it holds attention with cited reasons, what's measurable vs looked vs unknown, what to take and what
     not to copy (the creator's face, words, logos, music, footage are never copied: only the system), and how to turn
     it into a brief for the user's own video).
   - `report-template.md`: the report's sections, with the measured tables the script fills (`{{...}}` placeholders
     for numbers) and the parts the agent writes.
   - `briefs/teardown.md`: the agent's system prompt.
   - `examples/`: apply it to one itstundeanthony reel and one kamchai reel (one report each).
3. **Competitor analysis** → `out2/competitors/`: the method for comparing 2-6 accounts (3-5 reels each) for a
   business owner deciding how to make their own reels:
   - `COMPETITORS.md`: per account, its format (from the saved format) and its hook pattern; across accounts, a
     comparison table on the same measured fields, which devices are common to the category (table stakes) vs unique
     (differentiators), what no one does (gaps), and recommendations for the owner's own reels that stay original.
     Say what views/engagement data would add and that it is optional (often missing).
   - `report-template.md` and `briefs/competitor-analyst.md`.
   - `examples/`: one comparison of itstundeanthony vs kamchai vs TadClip's own reels (`kg01k`, `kg03`, `clinic-after`)
     treated as the owner's reels.
4. `out2/SOURCES.md`: every external source (new and kept), URL and what was used.
