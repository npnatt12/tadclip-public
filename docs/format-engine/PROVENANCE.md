# Format engine: provenance (clean room)

The method, the schema, the agent briefs and the two saved formats in `docs/format-engine/method/` were written in a
clean room: a separate Claude Code session that could not read Hypit or anything written about it. This file records
how, so anyone can check it.

## Who saw what

| side | saw Hypit's text? | wrote |
|---|---|---|
| this branch's main session (Claude, with the owner) | its LICENSE and SOURCE.md; file names; our own clone recipe, which paraphrases two of its guides. Not the guides themselves in this session | RESEARCH, ARCHITECTURE, this file, `format_spec.py` (signal processing: frame differences, OCR, face boxes, loudness), the contract, the evaluation tools |
| the clean-room session | no | `method/` (copied in unchanged from the room's `out/`) |

Only `CONTRACT.md` and `inputs/` crossed into the room:
- `CONTRACT.md`: what to write and the rules of the room (inputs, outputs, cite primary sources, no other product's guides);
- `inputs/FIELDS.md`: what `format_spec.py` measures;
- `inputs/specs/`: measurements and contact sheets of 10 reels (7 by two creators, 3 made by TadClip), version 1 of
  the measurer (before cuts were split into speaker and insert cuts);
- `inputs/reel-json.md`: TadClip's own builder reference (no mention of Hypit; checked with grep).

## How the room was sealed

- Its own folder, outside every repo: a private test folder.
- A separate, headless Claude Code process (`claude -p`, Opus) started in that folder with
  `--setting-sources project --strict-mcp-config`: no user settings, no MCP servers.
- Tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch. Bash, Skill, Agent and NotebookEdit denied (no shell, no
  skills such as the installed Hypit skill, no sub-agents).
- A PreToolUse hook (`tools/cleanroom/guard.py`) on every call: refuses any call whose input mentions Hypit or its old
  name Narratage, and any file path outside the room; logs every call to `<room>/.access.log`.
- The session's full transcript: `<room>/.session.jsonl`. Both logs stay with the private test material.

## Second session (revision, teardown, competitor analysis)

Same room, same seal, a new contract (`method/CONTRACT2.md`): revise the method with the version-2 measurer (speaker
cuts vs inserts), and write the video teardown (`method/rea/`) and competitor analysis (`method/competitors/`). New
inputs: the version-2 measurements, the creator studies' source lists, and the room's own first output. One call was
refused: the session tried to read its own saved web-fetch result, which Claude Code keeps outside the room; the guard
refused it (a path outside the room) and the session fetched again.

## Checks after

- `tools/format-eval/overlap.py`: share of the method's 8-word sequences found anywhere in Hypit's text, and the
  longest shared run (pass line fixed before writing: <= 1 % and < 15 words). Results in EVAL.md.
- This catches copying and close paraphrase, not shared ideas; the room's sealing is what keeps ideas independent.

## Limits, said plainly

- The model that wrote the method may have seen Hypit's public repository during its training. The room proves the
  session didn't read it; it can't prove the model never did. A lawyer weighs this.
- WebFetch can't be checked for pages that quote Hypit without naming it in the URL; the access log lists every page
  fetched, for a reviewer.

In this public copy, a private test brand's name is replaced and the room's access log and checksums are left out;
the private repository keeps the originals.
