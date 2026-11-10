# REA: reverse-engineering one short video (the teardown)

A person sends one reel they admire and asks "how is this made, and what can I learn from it?" The teardown agent
answers from `format_spec.py` v2 measurements, the contact sheet and (when available) a transcript. It produces one
report (`report-template.md`) that ends in a brief for the person's own video. It reuses the format engine's reading
rules (`../method/METHOD.md` part 1). It differs in that it explains one video to a human, while the engine saves
ranges for a machine.

## 1. Inputs and what each can tell you
| input | gives | cannot give |
|---|---|---|
| spec JSON (v2) | exact cut times split into shot cuts / insert changes, text events with time, place, size and colours, the face box, pauses | what the words mean, motion, sound |
| contact sheet | what each shot looks like: layout, type style, stickers, framing, pose jumps | anything between frames; it holds 24 frames at most, so it may stop early |
| transcript (optional: `transcribe.py`, or the user pastes it) | what is said and when: the claim, the question, the cue words | delivery (tone, emphasis) |
| study file (optional) | URL, uploader, views if known | usually views (often `null`) |

When there is no transcript, speech is **unknown**. Own captions and punch words are only a partial record of it
(Vision reads them approximately). Say so in the report.

## 2. Evidence levels (every line of the report carries one)
- **measured**: a spec field, quoted with its value.
- **derived**: computed from spec lists (a body cut rate, a beat length, a share).
- **looked**: read on the contact sheet, with the frame time.
- **inferred**: a reasoned reading of purpose ("this beat states the problem"). Always phrased as a reading and tied
  to measured or looked evidence.
- **unknown**: motion, sound, music, transitions, anything between frames, speech without a transcript, and outcomes
  (views, retention).
The report never turns an inferred reason into a fact, and never claims why a video performed well. Without
retention data nobody knows that. YouTube's retention report and Shorts' "viewed vs swiped away" exist precisely
because this is learned from viewer data, not from the file [S10][S16].

## 3. The procedure
**T1. Read the reel (METHOD R2–R7).** Run the reader's steps on this one reel: cut measurement and its audit (second
faces, graphic onsets, cuts to full-frame footage), own graphics vs footage text with roles, face and layout per
frame, pauses, and a one-line description of every frame.

**T2. Cut it into beats.** A beat boundary is any of the following:
(a) a layout shot cut (split ↔ full ↔ panel ↔ cutaway);
(b) the hook end (METHOD R2.2);
(c) the start of an own title, label or CTA that changes the topic;
(d) a pause longer than 0.6 s;
(e) a sentence that changes topic (transcript only).
Merge beats shorter than 1 s into a neighbour unless they are a device (such as the 1.97 s question shot). Viewers
perceive events at points where what comes next is no longer predictable, and these boundaries organise attention and
memory [S20]. That is why the teardown splits at visible changes and not at fixed seconds.

**T3. The second-by-second table.** Give one row per beat: `t0–t1 | layout | on screen (own graphics, footage) |
what is said (or unknown) | cuts in the beat (shot / insert) | job | evidence`. For the first 10 s, add a row per
second: what is on screen at each whole second, from `text.list` and the frame covering that second.

**T4. The hook (0 to the hook end).** Answer:
1. What is on screen at **frame 0**: the layout, the first own text (`text.first_seen`) and the face (yes/no).
2. **What the viewer is promised or asked** by 3 s: the proposition. TikTok's own guidance asks for it within 3 s and
   for the hook within 6 s [S9]. Report the measured time at which the promise is visible.
3. **The hook pattern** (closed list, add one only if none fits): `claim-on-screen` (the thing being judged is shown),
   `question` (an open question in text or speech), `promise-headline` (a stated benefit), `result-first` (the
   outcome shown before the how), `contrast` ("not X but Y"), `list-promise` ("2 types ..."), `pov`. Several can
   combine.
4. **Hook mechanics, measured:** the hook length, the cuts inside it (after the audit), the time of the first own
   text, how much of the frame the face takes, and the sheet frames that show it.

**T5. Each beat's job for the viewer.** Use one of: `promise`, `question`, `source` (where the claim comes from),
`context`, `step`, `proof` (evidence on screen), `payoff` (the result), `contrast`, `summary`, `cta`, `sign-off`.
Write one sentence on what the viewer gets from that beat and what open question carries them to the next. This is
`inferred` and must point at evidence (a frame, a text event, a transcript line).

**T6. Recurring devices.** List every treatment that appears twice or more (or once, as a structural element such as
the bar): what it is, when (times), where (y), its job, and the lever that would rebuild it (`reel-json.md`). Name
devices by function, never by the creator's wording.

**T7. Why it holds attention, with cited reasons.** Give at most five reasons. Each one names (a) the measured or
looked feature, (b) a mechanism from a cited source, and (c) its evidence level. Use cautious wording: "is consistent
with", "is designed to". Reasons the agent may use:
| feature in the reel | mechanism | source |
|---|---|---|
| the face on screen most of the time; text kept off it | faces draw early fixations | [S2] |
| an open question left visibly unresolved (a question pill, empty checkboxes, a "why" headline) | a felt information gap motivates closing it. **Hypothesis**: the source was reached only as a record | [S21] |
| frequent jump cuts that arrive with new content | within-scene edits often go unnoticed while viewers follow the content | [S19] |
| layout switches and section changes every few seconds | event boundaries organise attention and memory | [S20] |
| short punch words on spoken keywords, not full transcripts | signalling helps; redundant full text can compete with the picture | [S3] |
| the promise visible inside 3 s | the platform's own hook guidance | [S9] |
| the rhythm's long tail (p90) as well as its median | shot-length structure varies on purpose | [S1] |
Do not cite a reason the reel does not measurably show.

**T8. Measurable vs looked vs unknown.** Add a short three-column table so the reader sees the confidence of the
whole teardown at a glance.

**T9. What to take and what not to copy.**
- **Take the system.** Copyright protects expression, not ideas, procedures, systems or methods of operation (US 17
  U.S.C. §102(b) [S14]; the same exclusion in Thailand's Copyright Act §6 [S15]). A beat order, a layout grammar, a
  cut rhythm, a "question → test → verdict" structure and a device's *function* are the system. Write them as
  ranges and functions.
- **Never copy the expression or identity.** Do not copy the creator's face or likeness, their words or script, their
  series name or catchphrase, their logo or handle, their music (Meta: music needs proper permission and unlicensed
  music may be blocked, muted or removed [S22]), their footage or screen recordings, their exact combination of
  colours, type and placement that makes the reel recognisable as theirs, or other people's clips they show.
- **The platform prefers originals too.** Instagram recommends only the original of identical content and leaves
  accounts that mostly repost without material change out of recommendations [S17]. A near-copy is both a rights
  risk and a reach risk.
- The report states this in plain words and lists, per device, "take: <function>" and "make your own: <what to
  replace>". It is not legal advice. Specific rights questions go to a lawyer.

**T10. Turn it into a brief for the user's own video.** The brief has these parts:
1. **Your angle**: one line in the user's words (ask for it; never reuse the creator's topic line).
2. **The beat plan, scaled to your length**: the creator's beat proportions × the user's planned length, with each
   beat's job and target seconds. Keep the measured rates (shot cuts/min, insert changes/min), not the counts.
3. **What to film or gather**: per device, the material it `needs` (screen recordings, product footage, a result
   screenshot, an offer). Mark anything missing as "drop or replace".
4. **Your hook**: the hook pattern, the promise to show by 3 s, and a blank for the user's own line. Offer 2–3
   original line *shapes* (for example "Is <X> really <claim>? I tested it."), never the creator's words.
5. **Make it yours**: a distinct series name, a palette and a type choice, and one device the creator does not use
   (from T6 and from the gaps).
6. **Levers**: the reel.json levers for each device, so TadClip can build it. If the user has two or more reels from
   this creator, point them to the format engine (`../method/`) to save a reusable format instead. With one reel,
   ranges are ±25 % (`confidence: low`).

## 4. Rules of conduct
- Every number in the report comes from the spec or is derived from it, with the field named.
- Every claim about what something *looks like* cites a frame time.
- Words read by Vision are marked approximate, especially Thai.
- The report never guesses at views, retention or the creator's intent, beyond `inferred` beat jobs.
- The report names no one beyond the account handle the user gave, and quotes no more of the creator's on-screen
  words than needed to identify a device. Placeholders stand in for them in the brief.
