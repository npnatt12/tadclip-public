# Competitor analysis: comparing 2–6 accounts to decide how to make your own reels

A business owner names 2–6 accounts (3–5 reels each), usually including their own. The analyst agent tells them how
each account edits, what the category expects, where the accounts differ, what nobody does, and how the owner's own
reels should look so they meet the expectations, stand apart, and stay original. Everything is built on the format
engine (`../method/`) and the teardown (`../rea/`). This document adds the comparison layer.

## 1. Inputs
- Per reel: the `format_spec.py` v2 JSON + contact sheet, and the study file (URL, uploader, views if any).
- Per account: its saved format(s) from the format engine. If none exist, run the reader + spec-writer first (R1
  clustering decides whether an account has one format, several, or none).
- From the owner: their category and audience, language, the material they can produce (screen recordings, product
  footage, client results, an offer), and their own reels (treated as one more account).
- Optional: views and engagement (§6).

## 2. Per account: format and hook pattern
For each account write one block:
1. **Cluster result** (METHOD R1): which reels form the main format, which are variants or excluded, and why. An
   account whose reels share fewer than two devices has *no single format*. Say so instead of averaging.
2. **The format in one paragraph**, taken from the saved format's `summary` and key ranges.
3. **The hook pattern**: the pattern from REA T4's closed list (`claim-on-screen`, `question`, `promise-headline`,
   `result-first`, `contrast`, `list-promise`, `pov`), the measured hook end, what is on screen at frame 0, and when
   the promise is visible (≤ 3 s per the platform's own guidance [S9]).
4. **Signature devices** (signature = seen in ≥ 2/3 of member reels), named by function.

## 3. The comparison table (same measured fields for everyone)
One row per field, one column per account (min–max over that account's member reels; n in the header). Use the same
derived definitions for every account: own graphics only, body after the hook end, and the R2.3 corrections.
| group | field | source |
|---|---|---|
| length | `seconds` | measured |
| hook | hook end; hook pattern; first own text (`text.first_seen`) | derived / looked / measured |
| rhythm | body shot cuts/min; insert changes/min; `shot_median`; `shot_p90`; coincident | derived / measured / looked |
| text | own events/min; caption policy (all speech / splits only / none); punch-word share; accent colour | derived / looked |
| layout | `face.share`; `face.height` (shot scale); layout mix (full / split / panel / inset / cutaway) | measured / looked |
| voice | `audio.pauses_per_min`; `longest_pause` | measured |
| end | CTA type and timing; end card (yes/no); persistent brand chrome (yes/no) | measured / looked |
| data | views, engagement, n reels with data | study (optional) |
Never compare raw `text.share_of_time` or raw `cuts.per_min` across accounts: footage text and second-face insets
inflate them differently. Never compare `audio.lufs`.

## 4. Table stakes, differentiators, gaps
- **Table stakes**: a device or a field range present in **every** account (or in all but one when there are 5–6). A
  new entrant is expected to meet these. List each with its evidence per account.
- **Differentiators**: signature devices or out-of-band field values that belong to **one** account. These make an
  account recognisable. They are what the owner must **not** copy as a look (§5), though the *function* behind them
  may be learnt.
- **Shared by some**: devices in 2+ accounts but not all. These are options, not requirements.
- **Gaps**: things **no** account does that the evidence says matter, or that the owner can uniquely supply. Derive
  them in three ways: (a) a checklist of the method's functions (captions on speech, own proof on screen, a visible
  resolution or verdict, step markers, a CTA with a concrete offer, a hook under 3 s, face uncovered) with each
  account's status; (b) the owner's material that nobody else has; (c) accessibility: speech captions [S4][S12].
  A gap is an opportunity, not proof of demand. Say so.

## 5. Recommendations for the owner's reels (original by construction)
Write 4–7 recommendations. Each one names a **lever** (reel.json or a filming instruction), **why** (a table-stakes
item, a gap, or the owner's material), and **what keeps it original**. Rules:
1. **Meet the table stakes** in the owner's own look.
2. **Pick one or two gaps** the owner can fill with material only they have (their results, their screens, their
   clients' permission-cleared words).
3. **Learn functions from differentiators, never looks.** For example: "keep an open question visible until the
   answer", not "use a FACT/HYPE checkbox bar". Copyright protects expression, not systems or methods [S14][S15].
   Platforms recommend originals over near-copies [S17]. Never reuse another account's series name, catchphrase,
   handle, logo, footage, music [S22] or its identifying combination of colours, type and placement.
4. **Check the owner's own reels for accidental resemblance.** When an owner reel measures close to a competitor's
   saved format (the critic's score ≥ 0.70 against that format) *and* shares its identifying look, flag it and give
   the levers that change the look while keeping the system.
5. **Fit the owner's category.** A device from a different category transfers only if its `needs` can be met.
6. **Pace targets as ranges** (from the table), reached with take boundaries and clip changes, never by cutting words.
7. Recommendations are *conformance and positioning* advice. They never promise reach or views.

## 6. Views and engagement: optional, often missing
The study files usually have `views: null`. Without them, the analysis says **what each account does**, not **what
works**. If they are available:
- **Public counts** (views, likes, comments per reel) let you rank reels *within* an account and compare hook
  patterns inside it. Normalise by the account's median, not across accounts (follower counts and posting history
  differ).
- **The owner's own insights** go further. Instagram reports views (plays and replays), watch time including replays,
  and average watch time per initial view [S18]. YouTube Shorts reports the share of viewers who watched versus swiped
  away [S16], and a retention report shows where viewers leave [S10]. These link a hook or a beat to an outcome *for
  the owner's own reels*. Use them to test one change at a time.
- With 3–5 reels per account, any pattern is anecdotal. State n, and never present a correlation as a cause.
- If no data is available, write "no performance data; the comparison is descriptive" in the report header.

## 7. Procedure (analyst agent)
1. Check the inputs: 2–6 accounts, 3–5 reels each. Fewer reels → lower confidence, stated per account.
2. Run or load each account's reading and saved format; record clusters and exclusions.
3. Fill the per-account blocks (§2) and the comparison table (§3) from measured and derived values.
4. Classify devices into table stakes, shared, differentiators and gaps (§4), with evidence.
5. Score each owner reel against each competitor's saved format with the critic (C2, all four groups; list the group
   scores) to detect resemblance (§5.4).
6. Write the recommendations (§5) and the data note (§6). Fill `report-template.md`.
