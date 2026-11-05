"""Coach Q&A: a seated coach answers one question. The question card is the hook; the face stays clean (no running
captions); each point is a stock B-roll insert with a two-tier label, entered and left through a grainy colour swipe;
now and then a tilted keyword; a LINE CTA holds the back 35-40 %; a silent logo end card. Modelled on how
@clubgig_official edits (the grammar only, none of their brand or assets). Read SYSTEM.md first.

    import sys; sys.path.insert(0, "<skill>/recipes/coach-qa"); from coachqa import Coach
    C = Coach("$P", dur=46.9, title="R01", chin=1150)   # plate assets/talk.mp4 (muted), voice assets/voice.wav; chin = lowest chin y
    C.snaps([(2.0, 1.1), (10.7, 1.0), (13.5, 1.1)])                  # jump-cut reframes on the one plate, at take changes
    C.bug("YOUR\\nTAGLINE", "BRAND")                    # top chrome, whole reel (optional)
    C.qcard(0, 5.0, ["ข้อความ", "{ข้อความ}", "ข้อความ"])   # {line} = on the block; ("text", 1.2) = size x1.2
    C.broll(6.8, 10.0, "assets/broll/ignore.mp4", label=("ข้อความ", "ข้อความ"))
    C.broll(14.9, 19.7, [("assets/broll/a.mp4", 0), ("assets/broll/b.mp4", 2.4)],   # two clips under one label: (src, at s)
            label=("ข้อความ", "ข้อความ"))
    C.keyword(20.0, 22.4, [("ข้อความ", 20.0), ("ข้อความ", 20.5)])          # (line, its spoken onset)
    C.cta(27.5, ("ข้อความ", "ข้อความ"), "@handle")               # holds to the end card
    C.endcard(43.9, "BRAND", "YOUR TAGLINE")
    C.build()

All times are edit seconds (the cut's timeline). broll(..., media=[s, ...]) sets each clip's start inside its file;
swipe_in / swipe_out = False for a hard cut; C.swipe(t) alone puts the transition on any cut. Text is laid out line by
line by the author (Thai has no spaces to wrap on): a line shrinks to fit its band and raises below the house minimum.
build() writes index.html, build/beats.json (every beat with its keys, for snapshots) and build/coverage.txt (face time,
B-roll time, CTA share). Needs in $P: assets/talk.mp4, assets/voice.wav, the B-roll files. Fonts and SFX are copied.
"""
import json
import os
import random
import re
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
HOUSE = json.load(open(os.path.join(HERE, "house.json"), encoding="utf-8"))
PAL, LP, TY, KIT = HOUSE["palette"], HOUSE["layout_px"], HOUSE["type"], HOUSE["sound"]["kit"]
FPS = HOUSE["motion"]["fps"]
FONT = f"'{TY['family']}'"
BLOCK = {"red": PAL["block_red"], "maroon": PAL["block_maroon"]}
KW = re.compile(r"^\{(.*)\}$")
ROLE_DB = {"ui": -14, "whoosh": -12, "impact": -8, "meme": -3, "foley": -14, "riser": -12}   # vs voice p95 peak, as build.mjs


def fr(t):
    return round(round(t * FPS) / FPS, 4)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


_fc = {}


def adv(s, size, w=700):
    """advance width at weight w (basic layout: Thai marks are zero-advance, so this errs a little wide)"""
    from PIL import ImageFont
    if w not in _fc:
        f = ImageFont.truetype(os.path.join(SKILL, "templates/fonts", TY["file"]), 200)
        f.set_variation_by_axes([w])
        _fc[w] = f
    return _fc[w].getlength(s) * size / 200


def fit(text, size, maxw, min_size, w=700, pad=0):
    s = min(size, size * maxw / max(adv(text, size, w) + 2 * pad, 1e-3))
    if s < min_size:
        raise ValueError(f"line too long even at {min_size} px, split it: {text!r}")
    return round(s, 1)


def grain_png(path, n=384, seed=7):
    """a tileable grain tile (white/black specks on transparent) for the swipe; PIL, written once per project"""
    from PIL import Image
    rnd = random.Random(seed)
    im = Image.new("LA", (n, n), (0, 0))
    px = im.load()
    for _ in range(n * n // 9):
        x, y = rnd.randrange(n), rnd.randrange(n)
        px[x, y] = (255 if rnd.random() < 0.5 else 0, rnd.randrange(60, 170))
    im.save(path)


class Coach:
    """One Coach Q&A reel. Calls: snaps(), bug(), qcard(), broll(), swipe(), keyword(), cta(), endcard(), sfx(), build()."""

    def __init__(self, project, dur, title, plate="assets/talk.mp4", voice="assets/voice.wav", face=("50%", "30%"), lang="th",
                 chin=None, head=None):
        self.P = os.path.abspath(os.path.expanduser(project))
        self.dur, self.page_title, self.lang = dur, title, lang
        self.plate, self.voice, self.face = plate, voice, face
        self.chin = chin                                        # lowest chin y (px, after the snap zoom): chest-band text starts below it
        self.head = head                                        # highest hair y: the question card may go above it when the chest is short
        self.voice_dur = round(probe_dur(f"{self.P}/{voice}"), 2)
        self.H, self.JS, self.BEATS, self.SFX = [], [], [], []
        self.away, self.cta_t, self.end_t = [], None, dur
        self.band = []                                          # (t0, t1, what): one text unit in the chest band at a time
        self._id, self._track = 0, 10
        os.makedirs(f"{self.P}/assets/fonts", exist_ok=True)
        for f in (TY["file"], "LICENSE-Anuphan.txt"):
            if not os.path.exists(f"{self.P}/assets/fonts/{f}"):
                shutil.copy(f"{SKILL}/templates/fonts/{f}", f"{self.P}/assets/fonts/{f}")
        if not os.path.exists(f"{self.P}/assets/grain.png"):
            grain_png(f"{self.P}/assets/grain.png")

    # ------------------------------------------------------------ timeline primitives (same as caption-news)
    def nid(self, p="e"):
        self._id += 1
        return f"{p}{self._id}"

    def track(self):
        self._track += 1
        return self._track

    def set(self, sel, props, t):
        self.JS.append(f'tl.set("{sel}", {json.dumps(props, ensure_ascii=False)}, {fr(t):.4f});')

    def tween(self, sel, frm, to, t):
        self.JS.append(f'tl.fromTo("{sel}", {json.dumps(frm, ensure_ascii=False)}, '
                       f'{json.dumps({**to, "immediateRender": False}, ensure_ascii=False)}, {fr(t):.4f});')

    def beat(self, bid, keys):
        keys = sorted(round(k, 3) for k in keys)
        self.BEATS.append({"id": bid, "type": "beat", "label": bid, "t0": keys[0], "t1": keys[-1], "keys": keys})

    def clip(self, cid, t0, t1, z, style="", cls="clip"):
        return (f'<div id="{cid}" class="{cls}" data-start="{fr(t0):.4f}" data-duration="{fr(t1) - fr(t0):.4f}" '
                f'data-track-index="{self.track()}" style="z-index:{z};{style}">')

    def place(self, top, h, what):
        """chest-band top: the house position, pushed below the chin; refuses text past the Instagram UI (y 1470)"""
        if self.chin is not None:
            top = max(top, self.chin + 24)
        if top + h > 1470:
            raise ValueError(f"{what} ends at y {top + h:.0f} (> 1470, the Instagram UI): shorten it or lower chin")
        return top

    def sfx(self, name, t, db=0.0, ms=0.0, dur=None):
        """a sound at t, levelled by its role against this voice at build (ui -14, whoosh -12, impact -8 dB); db = offset"""
        self.SFX.append((name, t, db, ms, dur))

    # ------------------------------------------------------------ the plate
    def snaps(self, pairs):
        """jump-cut rhythm on one plate: [(t, scale)] instant reframes, origin on the face"""
        for t, s in pairs:
            self.set("#cam", {"scale": s}, t)

    # ------------------------------------------------------------ 1. the question card (the hook)
    def qcard(self, t0, t1, lines, block="red"):
        """2-3 centred lines in the chest band, white with a soft shadow; a line written "{...}" sits on the block (red or
        maroon); ("text", mult) scales a line. On from frame 0 with no sound; rises in staggered, wipes its block, fades."""
        Q = LP["qcard"]
        cid = self.nid("q")
        rows = []
        for ln in lines:
            text, m = (ln, 1.0) if isinstance(ln, str) else ln
            kb = KW.match(text)
            text = kb.group(1) if kb else text
            rows.append((text, fit(text, Q["size"] * m, Q["maxw"], Q["min_size"], pad=Q["block_pad_x"] if kb else 0), bool(kb)))
        lh = Q["lh"]
        h = sum(s * lh for _, s, _ in rows) + Q["line_gap"] * (len(rows) - 1)
        chest = Q["cy"] - h / 2 if self.chin is None else max(Q["cy"] - h / 2, self.chin + 24)
        if chest + h <= 1470:
            top = chest
        elif self.head is not None:                             # too tall for the chest band: above the head, shrunk to fit
            room = self.head - 24 - Q["top_min"]
            k = min(1.0, room / h)
            rows = [(tx, round(sz * k, 1), kb) for tx, sz, kb in rows]
            if min(sz for _, sz, _ in rows) < Q["min_size"]:
                raise ValueError(f"question card too tall above the head even at {Q['min_size']} px: use fewer lines")
            h *= k
            top = self.head - 24 - h
            print(f"question card above the head at {100 * k:.0f} % of the house size ({rows[0][1]} px)")
        else:
            top = self.place(chest, h, "question card (pass head= to allow above the head)")
        self.H.append(self.clip(cid, t0, t1, 30, f"left:0;width:1080px;top:{top:.0f}px", "clip stack"))
        for i, (text, s, kb) in enumerate(rows):
            rid = f"{cid}_{i}"
            ta = t0 + 0.06 * i
            if kb:
                self.H.append(f'<div id="{rid}" class="row"><span class="blk" style="font-size:{s}px;line-height:{lh};padding:0 {Q["block_pad_x"]}px">'
                              f'<i id="{rid}_b" class="blkbg" style="background:{BLOCK[block]}"></i><b>{esc(text)}</b></span></div>')
                self.tween(f"#{rid}_b", {"scaleX": 0}, {"scaleX": 1, "duration": 0.16, "ease": "power2.out"}, ta)
            else:
                self.H.append(f'<div id="{rid}" class="row"><span class="wt" style="font-size:{s}px;line-height:{lh}">{esc(text)}</span></div>')
            if t0 > 0:                                           # frame 0 shows the card complete: the hook is already up
                self.tween(f"#{rid}", {"y": 24, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.18, "ease": "power2.out"}, ta)
        self.H.append("</div>")
        self.tween(f"#{cid}", {"opacity": 1}, {"opacity": 0, "duration": 0.2, "ease": "power1.in"}, t1 - 0.2)
        if top >= (self.chin or 0):
            self.band.append((t0, t1, "question card"))
        self.sfx(KIT["hook"], t0 + 0.13, -4)
        self.beat(cid, [t0 + 0.3, t1 - 0.3])
        return cid

    # ------------------------------------------------------------ 2. the swipe transition
    def swipe(self, tc):
        """0.6 s centred on the cut at tc: blur whip of the outgoing picture, colour fields (yellow with a red-orange foot,
        cyan brush on white, blue, orange) with grain; the cut happens underneath; an iris opens in the orange."""
        sw = PAL["swipe"]
        sid = self.nid("sw")
        a = tc - 0.3
        self.H.append(self.clip(sid, a, tc + 0.32, 60, "left:0;top:0;width:1080px;height:1920px;overflow:hidden;pointer-events:none", "clip full")
                      + f'<i id="{sid}_y" class="fld" style="background:linear-gradient(180deg,{sw[0]} 0%,{sw[0]} 55%,{sw[1]} 100%)"></i>'
                      + f'<i id="{sid}_w" class="fld" style="background:#F4FBFC"></i>'
                      + f'<i id="{sid}_c" class="brush" style="background:linear-gradient(100deg,transparent 22%,{sw[2]} 38%,{sw[3]} 56%,transparent 74%)"></i>'
                      + f'<i id="{sid}_b" class="fld" style="background:{sw[4]}"></i>'
                      + f'<div id="{sid}_o" class="fld" style="overflow:hidden;background:transparent"><i id="{sid}_ir" class="iris" '
                        f'style="box-shadow:0 0 0 2400px {sw[5]}"></i></div>'
                      + f'<i id="{sid}_g" class="grain"></i></div>')
        for el, st in (("y", {"y": 1920}), ("w", {"opacity": 0}), ("c", {"x": -900, "opacity": 1}), ("b", {"opacity": 0}), ("o", {"opacity": 0})):
            self.set(f"#{sid}_{el}", st, a)                     # start states: nothing shows before its own tween
        self.tween("#stage", {"filter": "blur(0px)", "y": 0}, {"filter": "blur(16px)", "y": -90, "duration": 0.1, "ease": "power2.in"}, a)
        self.set("#stage", {"filter": "blur(0px)", "y": 0}, tc - 0.05)
        self.tween(f"#{sid}_y", {"y": 1920}, {"y": 0, "duration": 0.08, "ease": "power2.out"}, a + 0.08)
        self.tween(f"#{sid}_w", {"opacity": 0}, {"opacity": 1, "duration": 0.04, "ease": "none"}, a + 0.17)
        self.tween(f"#{sid}_c", {"x": -900, "rotation": -18}, {"x": 700, "rotation": -6, "duration": 0.2, "ease": "power1.out"}, a + 0.16)
        self.tween(f"#{sid}_b", {"opacity": 0}, {"opacity": 1, "duration": 0.05, "ease": "none"}, a + 0.3)
        self.set(f"#{sid}_y", {"opacity": 0}, a + 0.3)
        self.set(f"#{sid}_w", {"opacity": 0}, a + 0.36)
        self.set(f"#{sid}_c", {"opacity": 0}, a + 0.36)
        self.tween(f"#{sid}_o", {"opacity": 0}, {"opacity": 1, "duration": 0.04, "ease": "none"}, a + 0.38)
        self.set(f"#{sid}_b", {"opacity": 0}, a + 0.42)
        self.tween(f"#{sid}_ir", {"width": 0, "height": 0}, {"width": 2600, "height": 2600, "duration": 0.2, "ease": "power2.in"}, a + 0.42)
        self.tween(f"#{sid}_g", {"opacity": 0.45, "backgroundPosition": "0px 0px"},
                   {"opacity": 0.45, "backgroundPosition": "137px -211px", "duration": 0.6, "ease": "steps(9)"}, a)
        self.sfx(KIT["swipe"], a - 0.05)
        self.beat(sid, [a + 0.12, a + 0.25, a + 0.4, a + 0.5])
        return sid

    # ------------------------------------------------------------ 3. the B-roll insert with its two-tier label
    def broll(self, t0, t1, clips, label=None, media=None, swipe_in=True, swipe_out=True, block="maroon"):
        """full-screen stock cutaway(s) over the continuing voice. clips = "src" or [(src, at s from t0), ...]; label =
        (big line, small line on the block): lands as the iris opens, glitches out under the outgoing swipe."""
        if isinstance(clips, str):
            clips = [(clips, 0)]
        media = media or [0] * len(clips)
        bid = self.nid("b")
        self.away.append((t0, t1))
        for i, (src, at) in enumerate(clips):
            c0 = t0 + at
            c1 = t0 + clips[i + 1][1] if i + 1 < len(clips) else t1
            self.H.append(f'<video id="{bid}_v{i}" class="full brv" src="{src}" data-start="{fr(c0):.4f}" '
                          f'data-duration="{fr(c1) - fr(c0):.4f}" data-media-start="{media[i]:.3f}" data-track-index="{self.track()}" '
                          f'muted playsinline style="z-index:5"></video>')
            self.tween(f"#{bid}_v{i}", {"scale": 1.0}, {"scale": 1.06, "duration": c1 - c0, "ease": "none"}, c0)
        keys = [t0 + 0.2]
        if label:
            L = LP["label"]
            big, small = label
            sb = fit(big, L["big"], L["maxw"], 52)
            ss = fit(small, L["small"], L["maxw"], 32, pad=L["block_pad_x"])
            la = t0 + (0.12 if swipe_in else 0)
            lb = t1 - (0.2 if swipe_out else 0)
            h = sb * 1.3 + ss * 1.4 + L["gap"]
            self.H.append(self.clip(f"{bid}_l", la, lb, 40, f"left:0;width:1080px;top:{L['cy'] - h / 2:.0f}px", "clip stack")
                          + f'<div class="row"><span id="{bid}_lb" class="wt" style="font-size:{sb}px">{esc(big)}</span></div>'
                          + f'<div class="row" style="margin-top:{L["gap"]}px"><span class="blk" style="font-size:{ss}px;padding:0 {L["block_pad_x"]}px">'
                          f'<i id="{bid}_ls" class="blkbg" style="background:{BLOCK[block]}"></i><b>{esc(small)}</b></span></div></div>')
            self.tween(f"#{bid}_lb", {"scale": 1.12, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": 0.18, "ease": "back.out(1.6)"}, la)
            self.tween(f"#{bid}_ls", {"scaleX": 0}, {"scaleX": 1, "duration": 0.14, "ease": "power2.out"}, la + 0.1)
            self.sfx(KIT["label"], la + 0.05)
            if swipe_out:                                        # a 3-frame glitch: x jitter + slices, then gone
                for k, (dx, cp) in enumerate([(-14, "inset(0 0 52% 0)"), (18, "inset(38% 0 0 0)"), (-6, "inset(20% 0 30% 0)")]):
                    self.set(f"#{bid}_l", {"x": dx, "clipPath": cp}, lb - 0.1 + k / FPS)
            keys += [la + 0.3, lb - 0.15]
            self.band.append((la, lb, f"label {big!r}"))
        if swipe_in:
            self.swipe(t0)
        if swipe_out:
            self.swipe(t1)
        self.beat(bid, keys + [t1 - 0.4])
        return bid

    # ------------------------------------------------------------ 4. the floating keyword
    def keyword(self, t0, t1, lines, tilt=None):
        """1-2 big white lines over the chest, tilted; each reveals left to right on its spoken onset: lines = [(text, t)]"""
        K = LP["keyword"]
        kid = self.nid("k")
        rows = [(tx, t, fit(tx, K["size"], K["maxw"], K["min_size"])) for tx, t in lines]
        h = sum(s * K["lh"] for _, _, s in rows)
        top = self.place(K["cy"] - h / 2 + 30, h + 30, "keyword") - 30        # the -6 deg tilt lifts the left end ~30 px
        self.H.append(self.clip(kid, t0, t1, 35, f"left:0;width:1080px;top:{top:.0f}px;"
                                f"transform:rotate({tilt if tilt is not None else K['tilt_deg']}deg)", "clip stack"))
        for i, (tx, t, s) in enumerate(rows):
            self.H.append(f'<div class="row"><span id="{kid}_{i}" class="wt kwd" style="font-size:{s}px;line-height:{K['lh']}">{esc(tx)}</span></div>')
            self.sfx(KIT["keyword"], t - 0.05, -3)
            self.tween(f"#{kid}_{i}", {"clipPath": "inset(0% 100% 0% 0%)"}, {"clipPath": "inset(0% 0% 0% 0%)", "duration": 0.25,
                                                                           "ease": "power2.out"}, t)
        self.H.append("</div>")
        self.tween(f"#{kid}", {"opacity": 1}, {"opacity": 0, "duration": 0.15, "ease": "none"}, t1 - 0.15)
        self.band.append((t0, t1, f"keyword {lines[0][0]!r}"))
        self.beat(kid, [t + 0.3 for _, t, _ in rows] + [t1 - 0.2])
        return kid

    # ------------------------------------------------------------ 5. the LINE CTA
    def cta(self, t0, lines, handle, t1=None):
        """an orange speech bubble (1-2 lines) pointing down at a LINE badge + white handle pill; pops in with a pop and a
        whoosh, floats gently, holds to the end card (or t1)"""
        C = LP["cta"]
        t1 = t1 or self.end_t
        self.cta_t = t0
        self.band.append((t0, t1, "CTA"))
        sz = [fit(x, C["size"], C["w"] - 80, 30, w=500) for x in lines]
        hs = fit(handle, C["handle_size"], 420, 26)
        top = self.place(C["top"], sum(x * 1.25 for x in sz) + 40 + 34 + C["pill_h"], "CTA")
        self.H.append(self.clip("cta", t0, t1, 45, f"left:0;width:1080px;top:{top:.0f}px", "clip stack")
                      + f'<div id="cta_in" class="stack" style="position:relative;width:1080px">'
                      + f'<div class="bub" style="max-width:{C["w"]}px">' + "".join(
                          f'<div style="font-size:{s}px">{esc(x)}</div>' for x, s in zip(lines, sz)) + '<i class="tail"></i></div>'
                      + f'<div class="hrow"><span class="lineb" style="width:{C["logo"]}px;height:{C["logo"]}px">LINE</span>'
                        f'<span class="pill" style="height:{C["pill_h"]}px;font-size:{hs}px">{esc(handle)}</span></div></div></div>')
        self.tween("#cta_in", {"scale": 0.7, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": 0.3, "ease": "back.out(1.7)"}, t0)
        n = int((t1 - t0 - 0.4) // 2)
        for k in range(n):                                      # gentle float: 2 s up/down cycles, seek-safe tweens
            self.tween("#cta_in", {"y": 0 if k % 2 == 0 else -8}, {"y": -8 if k % 2 == 0 else 0, "duration": 2, "ease": "sine.inOut"},
                       t0 + 0.35 + 2 * k)
        self.sfx(KIT["cta_whoosh"], t0 - 0.12)
        self.sfx(KIT["cta"], t0)
        self.sfx(KIT["cta_pill"], t0 + 0.18, -2)
        self.beat("cta", [t0 + 0.4, t1 - 0.2])

    # ------------------------------------------------------------ chrome + close
    def bug(self, left, right, logo=None):
        """small white top chrome for the whole reel: a stacked caps tagline top left, a wordmark top right (logo = a
        white transparent PNG in the project, e.g. brand/<name>-wordmark-white.png, instead of the text)"""
        B = LP["bug"]
        rt = (f'<img src="{logo}" style="width:{B["logo_w"]}px;display:block;filter:drop-shadow(0 1px 3px rgba(0,0,0,.45))">'
              if logo else f'<div class="bugr" style="font-size:{B["size"] * 2}px">{esc(right)}</div>')
        self.H.append(self.clip("bug", 0, self.end_t, 50, f"left:{B['x']}px;right:{B['x']}px;top:{B['top']}px;display:flex;"
                                f"justify-content:space-between;align-items:flex-start")
                      + f'<div class="bugl" style="font-size:{B["size"]}px">{"<br>".join(esc(x) for x in left.split(chr(10)))}</div>'
                      + rt + '</div>')

    def endcard(self, t0, title, sub=None, logo=None):
        """white card, the wordmark (or logo = a dark transparent lockup PNG) fades and rises in with a soft ding; the reel
        ends here (dur)"""
        E = LP["end"]
        self.end_t = t0
        self.away.append((t0, self.dur))
        self.H.append(self.clip("end", t0, self.dur, 80, f"left:0;top:0;width:1080px;height:1920px;background:{PAL['end_bg']}")
                      + f'<div id="end_in" class="stack" style="position:absolute;left:0;width:1080px;top:{E["cy"]}px">'
                      + (f'<img src="{logo}" style="width:{E["logo_w"]}px;display:block">' if logo else
                         f'<div class="endt" style="font-size:{E["title"]}px">{esc(title)}</div>'
                         + (f'<div class="ends" style="font-size:{E["sub"]}px">{esc(sub)}</div>' if sub else "")) + "</div></div>")
        self.tween("#end_in", {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0, "duration": 0.5, "ease": "power2.out"}, t0 + 0.1)
        self.sfx(KIT["end"], t0 + 0.15, -4)
        self.beat("end", [t0 + 0.7])

    def voice_p95(self):
        """the p95 of 50 ms peak windows over the voice where it speaks (dBFS), as build.mjs measures it"""
        import array, math
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{self.P}/{self.voice}", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        x = array.array("f"); x.frombytes(raw)
        pk = sorted(m for m in (max(abs(v) for v in x[i:i + 800]) for i in range(0, len(x) - 800, 800)) if m > 0.01)
        return 20 * math.log10(pk[int(0.95 * (len(pk) - 1))])

    # ------------------------------------------------------------ write
    def build(self):
        P, DUR = self.P, self.dur
        b = sorted(self.band)
        for (a0, a1, an), (b0, b1, bn) in zip(b, b[1:]):
            if b0 < min(a1, self.end_t) - 0.01:
                raise ValueError(f"{an} ({a0:.2f}-{a1:.2f}) and {bn} (from {b0:.2f}) share the chest band: move one")
        aud = [f'<audio id="vo" src="{self.voice}" data-start="0" data-duration="{min(self.voice_dur, self.end_t):.2f}" '
               f'data-track-index="200" data-volume="1"></audio>']
        man = json.load(open(f"{SKILL}/library/sfx/manifest.json"))
        lens = {}
        p95 = self.voice_p95()
        for i, (f, t, db, ms, dur) in enumerate(sorted(self.SFX, key=lambda s: s[1])):
            v = round(min(1.0, 10 ** ((p95 + ROLE_DB.get(man[f].get("role"), -14) + db + 1) / 20)), 3)
            if man.get(f, {}).get("licensed") is False:
                raise ValueError(f"{f}: not licensed")
            os.makedirs(f"{P}/assets/sfx", exist_ok=True)
            dst = f"{P}/assets/sfx/{f}.wav"
            if not os.path.exists(dst):
                shutil.copy(f"{SKILL}/library/sfx/{man[f]['file']}", dst)
            lens.setdefault(f, round(probe_dur(dst), 3))
            t = max(0.0, t)
            aud.append(f'<audio id="sfx{i}" src="assets/sfx/{f}.wav" data-start="{fr(t):.4f}" '
                       f'data-duration="{min(dur or lens[f], DUR - t):.4f}" data-media-start="{ms:.3f}" '
                       f'data-track-index="{201 + i}" data-volume="{v}"></audio>')
        css = f"""
@font-face {{ font-family: {FONT}; src: url('assets/fonts/{TY['file']}') format('truetype'); font-weight: 100 900; }}
html, body {{ margin: 0; background: #000; }}
#root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: {FONT}; }}
.full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
video.full {{ object-fit: cover; }}
#cam {{ transform-origin: {self.face[0]} {self.face[1]}; }}
.clip {{ position: absolute; }}
i {{ font-style: normal; }}
.stack {{ display: flex; flex-direction: column; align-items: center; }}
.row {{ display: flex; justify-content: center; }}
.wt {{ display: inline-block; font-weight: 700; color: {PAL['white']}; line-height: 1.3; white-space: pre; text-shadow: {PAL['shadow']}; }}
.kwd {{ line-height: 1.25; }}
.blk {{ position: relative; display: inline-block; line-height: 1.4; white-space: pre; }}
.blkbg {{ position: absolute; inset: 0.06em 0 0.04em 0; transform-origin: 0 50%; }}
.blk b {{ position: relative; font-weight: 700; color: {PAL['white']}; }}
.fld {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; opacity: 1; }}
.brush {{ position: absolute; left: -200px; top: 300px; width: 1500px; height: 1300px; filter: blur(16px); }}
.iris {{ position: absolute; left: 50%; top: 55%; width: 0; height: 0; border-radius: 50%; transform: translate(-50%, -50%); }}
.grain {{ position: absolute; inset: 0; background: url('assets/grain.png') repeat; opacity: 0; mix-blend-mode: overlay; }}
.bub {{ position: relative; box-sizing: border-box; padding: 18px 40px 22px; border-radius: 28px; background: {PAL['cta_orange']};
       color: {PAL['white']}; font-weight: 500; line-height: 1.25; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,.25); }}
.bub div {{ white-space: pre; }}
.tail {{ position: absolute; left: 50%; bottom: -20px; width: 40px; height: 40px; margin-left: -20px; transform: rotate(45deg);
        background: {PAL['cta_orange']}; border-radius: 4px; z-index: -1; }}
.hrow {{ display: flex; align-items: center; gap: 16px; margin-top: 34px; }}
.lineb {{ display: flex; align-items: center; justify-content: center; border-radius: 24%; background: {PAL['line_green']}; color: #fff;
         font-family: Arial, sans-serif; font-weight: 900; font-size: 19px; letter-spacing: 0.02em; }}
.pill {{ display: flex; align-items: center; padding: 0 34px; border-radius: 999px; background: {PAL['pill']}; color: {PAL['ink']};
        font-weight: 700; letter-spacing: 0.02em; }}
.bugl {{ color: #fff; font-weight: 600; letter-spacing: 0.22em; line-height: 1.25; text-align: center; opacity: .9; text-shadow: 0 1px 4px rgba(0,0,0,.5); }}
.bugr {{ color: #fff; font-weight: 500; letter-spacing: 0.08em; line-height: 1; opacity: .9; text-shadow: 0 1px 4px rgba(0,0,0,.5); }}
.endt {{ color: {PAL['end_ink']}; font-weight: 500; letter-spacing: 0.1em; }}
.ends {{ color: {PAL['end_ink']}; font-weight: 600; letter-spacing: 0.3em; margin-top: 18px; }}
"""
        html = (f"""<!doctype html>
<html lang="{self.lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{esc(self.page_title)}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR:.2f}" data-fps="{FPS}">
<div id="stage" class="full" style="z-index:1">
<div id="cam" class="full"><video id="vt" class="full" src="{self.plate}" data-start="0" data-duration="{self.end_t:.2f}" data-track-index="0" muted playsinline></video></div>
""" + "\n".join(h for h in self.H if 'class="full brv"' in h) + "\n</div>\n"
                + "\n".join(h for h in self.H if 'class="full brv"' not in h) + "\n" + "\n".join(aud)
                + '\n<script>\nwindow.__timelines = window.__timelines || {};\nconst tl = gsap.timeline({ paused: true });\n'
                + "\n".join(self.JS) + f'\ntl.set({{}}, {{}}, {DUR:.2f});\nwindow.__timelines["main"] = tl;\n</script>\n</div>\n</body>\n</html>\n')
        open(f"{P}/index.html", "w").write(html)
        os.makedirs(f"{P}/build", exist_ok=True)
        json.dump({"fps": FPS, "beats": sorted(self.BEATS, key=lambda b: b["t0"]),
                   "shots": [{"t0": a, "t1": b} for a, b in sorted(self.away)]},
                  open(f"{P}/build/beats.json", "w"), indent=1, ensure_ascii=False)
        away = sum(b - a for a, b in self.away)
        talk = self.end_t
        lines = [f"face on screen: {DUR - away:.2f} s of {DUR:.2f} s ({100 * (DUR - away) / DUR:.0f} %); B-roll + end card {away:.2f} s",
                 (f"CTA from {self.cta_t:.2f} s = {100 * self.cta_t / talk:.0f} % of the talk, on {talk - self.cta_t:.1f} s "
                  f"({100 * (talk - self.cta_t) / talk:.0f} %; house 35-40 %)") if self.cta_t is not None else "CTA: none (the style wants one)",
                 f"beats: {len(self.BEATS)}; sfx: {len(self.SFX)}; html {len(html) // 1024} KB"]
        open(f"{P}/build/coverage.txt", "w").write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return lines


if __name__ == "__main__":
    print(__doc__)
