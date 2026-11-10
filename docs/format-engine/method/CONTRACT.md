# Contract: the format engine's method (clean room)

You are writing, from first principles and primary sources, the method a group of agents uses to (1) read the editing
format of a creator's short vertical videos from measurements, (2) save it as a reusable format, (3) decide which parts
of it suit a different talking-head clip, and (4) score a finished reel against it. The product is TadClip, an editor
that turns a raw talking-head recording into a finished 1080x1920 reel (Thai first, English too).

## Rules of this room
- Work only inside this folder. Everything you need is in `inputs/`. Write only into `out/`.
- Write in your own words. Where you rely on a claim about attention, retention, readability or platform behaviour,
  cite a primary source you found yourself (a paper, a platform's own documentation or creator guidance, a standard)
  in `out/SOURCES.md` with its URL and what you took from it.
- Do not look up, quote or paraphrase any existing video-agent product's guides or prompts. Methods are built here.

## Inputs (`inputs/`)
- `specs/*.json` + `specs/*.jpg`: measurements of real reels by `format_spec.py` (described in `inputs/FIELDS.md`), with a
  contact sheet per reel (one frame per shot, its start time under it). `creator-<name>-<id>` are other creators' reels;
  `kg*` and `clinic-after` are reels TadClip itself made.
- `reel-json.md`: what TadClip's builder can do (the levers a format can be expressed with).

## Outputs (`out/`)
1. `METHOD.md`: the method, in four parts: read, save, fit, score. Every rule names the measured fields it uses
   (`cuts.per_min`, `text.zones`, ...) and the builder lever it sets. Say what can't be measured and has to be looked at
   on the contact sheet, and how to look. Keep it under 400 lines.
2. `format.schema.json`: JSON Schema of a saved creator format: each field with a measured range (not a single value),
   its source field in the spec, and the reel.json lever it maps to. Include `devices`: recurring treatments (e.g. a
   card on the chest, a photo beside the face) with when they occur.
3. `briefs/`: one short system prompt per agent: `reader.md`, `spec-writer.md`, `fit-checker.md`, `critic.md`.
4. `SOURCES.md`: every external source, with URL and what was used.
5. `formats/`: apply your method to the inputs: one saved format per creator in `inputs/specs` (itstundeanthony,
   kamchai), as JSON valid against your schema, and a one-paragraph reading of each.
