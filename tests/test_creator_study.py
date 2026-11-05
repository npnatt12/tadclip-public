"""python3 tests/test_creator_study.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from creator_study import shorts_url, top_by_views

assert shorts_url("@its.tunde-a_1") == "https://www.youtube.com/@its.tunde-a_1/shorts"
assert shorts_url("https://www.instagram.com/reel/abc/") is None and shorts_url("@bad/path") is None
got = top_by_views([{"url": "a", "view_count": 5}, {"url": "b", "view_count": None}, {"url": "c", "view_count": 9}], 2)
assert [e["url"] for e in got] == ["c", "a"]
print("ok")
