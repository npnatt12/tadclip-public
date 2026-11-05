"""broll_fetch: one bad download doesn't end the batch, a retry is tried, and list copes with photo rows. python3 tests/test_broll_fetch.py"""
import contextlib, io, json, os, sys, tempfile, types, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import broll_fetch as B

with tempfile.TemporaryDirectory() as d:
    json.dump([{"id": "ph1", "beat": None, "kind": "photo", "w": 4000, "h": 6000, "fps": None, "duration": None}], open(os.path.join(d, "manifest.json"), "w"))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        B.cmd_list(types.SimpleNamespace(dir=d))
    assert "ph1" in out.getvalue()

    err = lambda: urllib.error.HTTPError("u", 403, "Forbidden", {}, None)
    calls = {}

    def download(url, dest):
        calls[url] = calls.get(url, 0) + 1
        if url == "dead" or (url == "flaky" and calls[url] == 1):
            raise err()
        open(dest, "wb").write(b"x")
        return 1, True

    B.parse = lambda ref: ("pexels", ref, None)
    def original_url(src, vid):  # the lookup answers 403 too (2026-11-05, pexels:7594018)
        if vid == "nolookup":
            raise err()
        return vid

    B.original_url = original_url
    B.download = download
    B.probe = lambda f: {"w": 2160, "h": 3840, "fps": 30, "duration": 5, "hdr": False, "full_screen_ok": True}
    B.look_frames = lambda f, stem, dur: []
    B.time.sleep = lambda s: None
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            B.cmd_get(types.SimpleNamespace(dir=d, refs=["dead", "nolookup", "flaky", "good"], min=1080, beat=None))
        except SystemExit as e:
            assert e.code == 0, "some clips landed"
    assert calls["dead"] == 2 and calls["flaky"] == 2 and calls["good"] == 1, calls
    assert "pdead" in out.getvalue() and "pnolookup" in out.getvalue() and {r["id"] for r in json.load(open(os.path.join(d, "manifest.json")))} >= {"pflaky", "pgood"}
print("ok")

# a blank KEY= line in the .env template is no key: the reader must not take the next line instead
with tempfile.TemporaryDirectory() as d:
    os.mkdir(os.path.join(d, "scripts"))
    open(os.path.join(d, ".env"), "w").write("PEXELS_API_KEY=\n\n# a comment\n")
    B.__file__ = os.path.join(d, "scripts", "broll_fetch.py")
    os.environ.pop("PEXELS_API_KEY", None)
    try:
        raise AssertionError(f"read a blank key as {B.env_key('PEXELS_API_KEY')!r}")
    except SystemExit:
        pass
