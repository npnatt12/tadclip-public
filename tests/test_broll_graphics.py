"""The motion score skips a logo end card, but still counts a static slide inside the talk. python3 tests/test_broll_graphics.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from broll_qa import endcard_start, long_graphics

spec = {"outro": 2.2, "beats": [{"type": "impact"}, {"type": "endcard", "at": "outro+0"}]}
assert abs(endcard_start(spec, 93.2) - 91.0) < 1e-6
assert endcard_start({"outro": 2.2, "beats": [{"type": "impact"}]}, 93.2) == float("inf"), "no end card: nothing is exempt"

R = [("G", 18.0, 18.4, 0, 0), ("S", 18.4, 40.0, 0, 0), ("G", 40.0, 43.0, 0, 0), ("S", 43.0, 91.0, 0, 0), ("G", 91.2, 93.2, 0, 0)]
assert long_graphics(R, 91.0) == [(40.0, 43.0)], "the end card goes, the slide in the talk stays"
assert long_graphics(R, float("inf")) == [(40.0, 43.0), (91.2, 93.2)]
print("ok")
