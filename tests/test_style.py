"""Style loading: old names still resolve and "extends" layers presets, the same in Python and JS. python3 tests/test_style.py"""
import json, os, pathlib, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
from reelproj import load_project, load_style

JS = """import {loadStyle} from %r; try { console.log(JSON.stringify(loadStyle(process.argv[1], process.argv[2]))) } catch (e) { console.log("ERR " + e.message) }""" % pathlib.Path(ROOT, "scripts/lib/style.mjs").as_uri()   # a file:// URL: Node won't import a bare Windows path
js = lambda skill, name: subprocess.run(["node", "--input-type=module", "-e", JS, skill, name], capture_output=True, text=True).stdout.strip()

assert load_style(ROOT, "icarus") == load_style(ROOT, "clubgig") and load_style(ROOT, "clubgig")["impact"]["look"] == "stair"
assert json.loads(js(ROOT, "icarus")) == load_style(ROOT, "clubgig")

with tempfile.TemporaryDirectory() as d:
    os.mkdir(os.path.join(d, "styles"))
    w = lambda n, o: json.dump(o, open(os.path.join(d, "styles", n + ".json"), "w"))
    w("clubgig", {"zoom": {"base": 1.3, "faceAt": [0.5, 0.4]}, "impact": {"look": "stair"}})
    w("over", {"extends": "icarus", "_about": "x", "zoom": {"base": 1.1}})
    want = {"zoom": {"base": 1.1, "faceAt": [0.5, 0.4]}, "impact": {"look": "stair"}}
    assert load_style(d, "over") == want and json.loads(js(d, "over")) == want
    w("loop", {"extends": "loop"}); w("gone", {"extends": "nope"})
    for bad in ("loop", "gone"):
        try:
            load_style(d, bad); raise SystemExit(f"{bad} should fail")
        except ValueError:
            pass
        assert js(d, bad).startswith("ERR"), bad
    assert load_style(d, "missing") == {} and js(d, "missing") == "null"
    json.dump({"style": "icarus", "takes": [{"a": 0, "b": 1}]}, open(os.path.join(d, "reel.json"), "w"))
    pr = load_project(d, skill=d)
    assert pr.raw["style"] == "clubgig" and pr.spec["impact"]["look"] == "stair"
print("ok")
