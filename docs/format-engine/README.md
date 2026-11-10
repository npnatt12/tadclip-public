# Format engine (experimental)

A format-reading engine for TadClip that a paid edition could ship: it measures a creator's reels, saves their format
as numbers and devices, decides what suits a new clip, and scores the result. Written without Hypit's text or code.

| file | what |
|---|---|
| [RESEARCH.md](RESEARCH.md) | open-source tools and official APIs, with licences checked at the source |
| [ARCHITECTURE.md](ARCHITECTURE.md) | scout → measurer → reader → spec writer → fit checker → critic |
| [FIELDS.md](FIELDS.md) | what `scripts/format_spec.py` measures |
| [method/](method/) | the clean-room method, schema, agent briefs, two saved formats, sources (from the room) |
| [PROVENANCE.md](PROVENANCE.md) | how the clean room was sealed and what crossed into it |
| [EVAL.md](EVAL.md) | the scores, and what still needs people |

Try it: `python3 scripts/format_spec.py <reel.mp4> --out spec.json --sheet sheet.jpg` (self-test: `--check`).
