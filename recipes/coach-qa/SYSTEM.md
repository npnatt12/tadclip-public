# Coach Q&A as a system

Same method as recipes/caption-news/SYSTEM.md: the invariants and the house look make it Coach Q&A, the slots follow the
content, catalog.json records what each reel used. Modelled on @clubgig_official (Thai relationship coach, 141K), studied
2026-10-31 from 7 reels. The
grammar only: none of their brand, footage, transition asset or copy.

## Thesis
**One question a viewer is already asking, answered by a calm expert to camera. The question on screen is the hook;
the face stays clean; each point becomes a recognisable scene (stock B-roll with a two-tier label) behind a colour swipe;
the offer sits on screen for the whole back third.**

## Invariants (never change: this is the style)
1. **The question is the hook.** Frame 0 shows the question complete (2-3 lines, one on a block), held ~5 s while the
   answer starts. No greeting, no name.
2. **No running captions.** Only the question card, B-roll labels, at most two keywords and the CTA ever carry text.
3. **One B-roll insert per point**, 2-5 s, voice continuing; each with a two-tier label naming the point.
4. **Every insert enters and leaves through the colour swipe** (the same one, every time) with a whoosh.
5. **Tight A-roll:** pauses cut to < 0.2 s (the raw cut), jump-cut reframes every 2-5 s (`snaps`).
6. **The CTA owns the back 35-40 %** of the talk, from ~60 % or the pivot sentence to the end card.
7. **A silent white logo end card**, ~2.5-3 s.
8. **One text unit in the chest band at a time** (build() refuses overlaps).

## House look (fixed: house.json)
Anuphan 700/500 (Thai + Latin; Kanit-like weight is the reference, swap in house.json), white type with a soft shadow,
block red #C53E2B (question) / maroon #7A1F35 (labels), CTA orange, LINE green, the swipe palette, the chest band
(y 1000-1450), the motion constants and the sound kit (whoosh-cine swipe, pop-3 + whoosh-2 CTA, nothing else, no bed).

## Slots and their generators

| slot | its job | generator: the question that fills it from a new script |
|---|---|---|
| S1 question card | the hook | what is the viewer's question in 2-3 short lines, and which line carries the sting (on the block)? red or maroon? a quoted word? |
| S2 points | B-roll + label per point | which 2-3 sentences are the points? for each: what scene would a viewer recognise (stock), the big line (2-4 words) and the small line (the consequence)? |
| S3 keywords | 0-2 stresses | which phrase does the speaker lean on that is NOT already a label? one or two lines, on its onset |
| S4 CTA | the offer | where does the talk pivot to advice (or ~60 %)? the bubble text (1-2 lines) and the handle |
| S5 close | end card | wordmark + tagline |
| chrome | bug | tagline + wordmark, or none |

## Planning procedure
1. The raw cut first (take-selection.md: rawcut_prep -> ... -> assemble; pauses < 0.2 s): assets/talk.mp4 + voice.wav,
   build/words.cut.json for the onsets.
2. Write the plan as a docstring at the top of $P/tools/build.py: the question, the points with their onset times, the
   keywords, the CTA start. Points land on the onset of the sentence that names them.
3. Fetch B-roll per point (`broll_fetch.py`, Pexels / Wikimedia Commons; stock is ALLOWED in this style, the owner 2026-10-31), run
   `broll_vision.py picks` and WAIT for the user's yes; people checks apply.
4. `snaps` at every take change (1.0 <-> 1.1).
5. Run build.py (it refuses chest-band overlaps and lines below the minimum size), `hf.sh lint` (0 errors; the
   nested-structure warnings are expected), snapshot the question card, every swipe mid-way (cut-0.2, cut, cut+0.1),
   every label, keyword and the CTA.
6. `finals.py preview ... --style "Coach Q&A"` and WAIT for the user's OK.

## Rejected (do not copy)
- The reference's brand (name, wordmark, tagline), its footage, its transition asset and its exact copy.
- Burned-in running captions: the reference has none; adding them makes it a different style.

## Not yet built
- A two-person variant (the account occasionally runs a co-host format).
- Kanit as a shipped font (needs downloading; Anuphan ships).

## Changelog
- v0.1 (2026-10-31): builder coachqa.py (class Coach): qcard, swipe, broll + label, keyword, cta, bug, endcard; proved on
  an 11.5 s local test (references/clubgig/coachqa-test, never shipped).
- v0.2 (2026-10-31): first real reel (KG01). `Coach(..., chin=<px>)` pushes
  chest-band text below the chin and refuses anything past y 1470 (the Instagram UI); house shadow tightened for light
  clothing (white type on a cream jacket was unreadable with the soft shadow); bug text gets a small shadow.
