# Video teardown (REA) and competitor analysis

Reports, not edits: for someone who wants to learn from a video, or decide how to make their own reels against the
accounts they compete with. Built on the format engine (`docs/format-engine/`): every video is measured first, then an
agent reads the numbers with the contact sheet and the timeline. The method and the agents' briefs are TadClip's own,
written in a clean room (`docs/format-engine/PROVENANCE.md`).

**Never copied into the user's work:** the creator's face, words, logos, music or footage. A teardown explains the
system; recommendations stay original.

## Teardown: "วิเคราะห์คลิปนี้", "ทำไมคลิปนี้ปัง", "reverse-engineer this video"

1. **Get the video:** a file they gave, or `python3 $S/scripts/creator_study.py <link> --out $P/study` (one link, the
   user's own request; Instagram/TikTok profiles are listed in their own logged-in browser, never scraped in bulk).
2. **Measure and draw:** `python3 $S/scripts/video_rea.py teardown <video> --out $P/rea` → per video `spec.json`,
   `sheet.jpg` (a frame per shot), `timeline.png` (speaker cuts, inserts, text by zone) and `report.md` (the template
   with every measured number filled).
3. **Read and write** the rest of `report.md` by `docs/format-engine/method/rea/briefs/teardown.md` (method:
   `rea/REA.md`): structure second by second, the hook, each beat's job for the viewer, recurring devices, why it holds
   attention (with the reasons the method cites), what is measured vs looked vs unknown, what to take and what not to
   copy, and a brief for their own video. Examples: `rea/examples/`.
4. **Show** the report (and the timeline image); offer the next step: clone route B (`recipes/clone/README.md`) to film
   their own version, or a creator style (route A) for their next edit.

## Competitor analysis: "วิเคราะห์คู่แข่ง", "competitor analysis", "compare @a @b @c"

1. **Accounts:** 2-6 accounts, 3-5 reels each where someone talks to camera (most-viewed recent ones, read from each
   profile in the user's own browser), plus the user's own reels if they have some ("you").
2. **Fetch and measure:** `creator_study.py` per account into `$P/compete/<name>/`, then
   `python3 $S/scripts/video_rea.py competitors <name>=$P/compete/<name> ... --out $P/compete/report` →
   `compare.md` (the template with the side-by-side table filled), `compare.json`, a teardown folder per reel.
3. **Read and write** by `docs/format-engine/method/competitors/briefs/competitor-analyst.md` (method:
   `competitors/COMPETITORS.md`): each account's format and hook pattern, what everyone in the category does (table
   stakes), what's unique (differentiators), what no one does (gaps), and recommendations for the user's own reels that
   stay original. Views and engagement are optional extra evidence: say when they're missing. Example:
   `competitors/examples/`.
4. **Show** `compare.md`; offer to save the strongest format as a creator style, or to edit their next clip with it.
