#!/usr/bin/env python3
"""Clean-room guard: a Claude Code PreToolUse hook for the session that writes the format engine's method
(docs/format-engine/PROVENANCE.md). Every tool call is logged to <room>/.access.log; a call is refused (exit 2) when
it mentions Hypit (or its old name, Narratage) anywhere in its input, or when a file tool reaches outside the room.
    settings: {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "python3 guard.py <room>"}]}]}}"""
import json, os, re, sys, time
room = os.path.realpath(sys.argv[1]); call = json.load(sys.stdin)
tool, inp = call.get("tool_name", ""), call.get("tool_input", {})
blob = json.dumps(inp, ensure_ascii=False)
why = None
if re.search(r"hypit|narratage", blob, re.I): why = "names Hypit: this room may not read or search it"
for k in ("file_path", "path", "notebook_path"):
    p = inp.get(k)
    if p and not os.path.realpath(os.path.expanduser(p)).startswith(room): why = f"{k} outside the clean room: {p}"
if tool == "Glob" and inp.get("pattern", "").startswith(("/", "~", "..")) and not os.path.realpath(os.path.expanduser(inp["pattern"].split("*")[0])).startswith(room):
    why = "glob outside the clean room"
with open(os.path.join(room, ".access.log"), "a") as f:
    f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": tool, "input": blob[:400], "refused": why}, ensure_ascii=False) + "\n")
if why: print(f"clean room: refused, {why}", file=sys.stderr); sys.exit(2)
