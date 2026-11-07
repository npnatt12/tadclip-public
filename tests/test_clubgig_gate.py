"""One prompt must give a whole ClubGig reel: a reel without the devices can't reach a render, and no Pexels key can't stop the stock. python3 tests/test_clubgig_gate.py"""
import importlib.util, json, os, subprocess, sys, tempfile, types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = """import {clubgigMissing} from %r; const r = JSON.parse(process.argv[1]);
console.log(JSON.stringify(clubgigMissing(r, r.beats, (x) => x - (r.takes?.[0]?.a ?? 0), r.speech ?? 90, r.sfx ?? 30)))""" % os.path.join(ROOT, "scripts", "lib", "clubgig_gate.mjs")
missing = lambda reel: json.loads(subprocess.run(["node", "--input-type=module", "-e", JS, json.dumps(reel)], capture_output=True, text=True, check=True).stdout)

gallery = json.load(open(os.path.join(ROOT, "examples", "gallery", "clubgig.reel.json")))
assert missing(gallery) == [], missing(gallery)

bare = {"style": "clubgig", "beats": [], "sfx": 0}
gone = missing(bare)
for want in ("hook card", "hook stock", "popups", "swiped stock", "brand chrome", "LINE CTA", "end card", "sound"):
    assert any(want in m for m in gone), (want, gone)

assert not any("LINE CTA" in m for m in missing({**bare, "omit": ["linecta"]})), "the user may drop a device by name"
assert missing({**gallery, "beats": [b for b in gallery["beats"] if b["type"] != "endcard"]}) == ["end card (endcard)"]

# finals: the report from build.mjs holds the preview and the master
spec = importlib.util.spec_from_file_location("finals", os.path.join(ROOT, "scripts", "finals.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
calls = []
F.hf_render = lambda *a: calls.append(a) or False
with tempfile.TemporaryDirectory() as d:
    os.mkdir(os.path.join(d, "build"))
    open(os.path.join(d, "index.html"), "w").write("x")
    report = os.path.join(d, "build", "build_report.json")
    r = {"project": d, "out": os.path.join(d, "finals"), "name": "t"}
    json.dump({"missing": ["end card (endcard)"]}, open(report, "w"))
    F.preview(r); F.render(r)
    assert not calls, "an incomplete reel must not render"
    F.preview(r, force=True)
    assert len(calls) == 1, "--force is the way past it"
    json.dump({"missing": []}, open(report, "w"))
    F.preview(r)
    assert len(calls) == 2

# no key: the stock search moves to Mixkit instead of stopping
spec = importlib.util.spec_from_file_location("broll_fetch", os.path.join(ROOT, "scripts", "broll_fetch.py"))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
def no_key(name):
    raise SystemExit("no key")
B.env_key = no_key
B.http = lambda url: types.SimpleNamespace(read=lambda: b'<a href="/free-stock-video/cup-of-coffee-236/">')
out = []
B.print = lambda *a, **k: out.append(" ".join(map(str, a)))
B.cmd_search(types.SimpleNamespace(pexels=True, words=["coffee"], n=3, any=False))
assert any("mixkit:236" in o for o in out), out
print("ok")
