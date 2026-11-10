#!/usr/bin/env python3
"""The user's OWN brand on their reels: whatever they put in ~/TadClip/brand/ (docs/BRAND-KIT.md).
(Not brand_kit.py: that one pulls the brand of a product a reel talks about, into brand/kit.json.)

Input, all optional: a logo (any image; a LINE or Facebook profile picture works; a light/white version for over the
video, a dark one for the white end card), a brand sheet or style guide (an image or PDF that lists colour codes: every
code is read), one screenshot of their page, brand.txt (colours, font, name, tagline, LINE), a .ttf/.otf font.
HEIC (iPhone), SVG, PDF, GIF, TIFF are converted with macOS sips / Quick Look into brand/.converted (hidden). Output in <project>/brand/: own-logo-video.png (top
right, over the footage), own-logo-card.png (white end card), own.json (colours, font, words) that build.mjs lays over
the style, own-metrics.json for a font of their own. Every fix is one plain Thai line in "notes"; nothing is refused.

  python3 own_brand.py <project> [--from DIR]   DIR: default $TADCLIP_DIR/brand, else ~/TadClip/brand
  python3 own_brand.py --show [--from DIR]      the summary the app shows (JSON), writes nothing
  python3 own_brand.py --check                  self-test on made-up brands
No folder, or an empty one: says so and exits 0 (the style's own brand, ClubGig, stays).
Needs only Pillow and numpy (both in setup.sh)."""
import json, os, re, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THAI_FONTS = os.path.join(SKILL, "library", "fonts", "thai")
IMG = (".png", ".jpg", ".jpeg", ".webp")
CONVERT = (".heic", ".heif", ".svg", ".pdf", ".gif", ".tif", ".tiff", ".bmp")
FONT = (".ttf", ".otf")
YELLOW = "#FFE11A"   # ClubGig's highlighted word, kept when the brand has no second colour

# ---------- colour: sRGB <-> OKLab/OKLCH, WCAG contrast ----------
def hex2rgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255
def rgb2hex(c): return "#" + "".join(f"{int(round(min(1, max(0, v)) * 255)):02X}" for v in c)
def lin(c): c = np.asarray(c, float); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def unlin(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
def oklab(rgb): return np.cbrt(lin(rgb) @ M1.T) @ M2.T
def from_oklab(lab): return unlin(((lab @ np.linalg.inv(M2).T) ** 3) @ np.linalg.inv(M1).T)
def lch(rgb): L, a, b = oklab(rgb); return float(L), float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a)) % 360)
def from_lch(L, C, H):
    for _ in range(40):   # pull chroma in until it fits sRGB
        c = from_oklab(np.array([L, C * np.cos(np.radians(H)), C * np.sin(np.radians(H))]))
        if (c >= -1e-4).all() and (c <= 1 + 1e-4).all(): break
        C *= 0.9
    return np.clip(c, 0, 1)
def lum(rgb): return float(lin(rgb) @ [0.2126, 0.7152, 0.0722])
def contrast(a, b): x, y = sorted([lum(a), lum(b)]); return (y + 0.05) / (x + 0.05)
def hue_gap(a, b): d = abs(lch(a)[2] - lch(b)[2]); return min(d, 360 - d)
WHITE, INK = np.ones(3), hex2rgb("#111111")

def plate_from(primary):
    """the popup plate: the brand colour, darkened only as much as white text needs (WCAG 4.5:1); plate2 one step lighter
    (the stair), or darker when there's no room above."""
    L, C, H = lch(primary); p = primary
    while contrast(WHITE, p) < 4.5 and L > 0.05: L -= 0.01; p = from_lch(L, C, H)
    L2 = L + 0.07; p2 = from_lch(L2, C, H)
    while contrast(WHITE, p2) < 4.5 and L2 > L: L2 -= 0.01; p2 = from_lch(L2, C, H)
    if L2 - L < 0.03: p2 = from_lch(L - 0.06, C, H)
    return p, p2

def ink_for(bg, dark=None):
    """text on a plate: white, else the brand's own dark colour, else near-black, whichever first reaches WCAG 4.5:1; None
    when none does (a mid-tone: the plate is darkened instead). 11-10 test: a clinic's light cyan #00CCFF was darkened to teal
    for white text, so the reel read dark blue; their own Oxford Blue on the cyan is 5.7:1 and keeps the cyan."""
    return next((c for c in [WHITE] + ([dark] if dark is not None else []) + [INK] if contrast(c, bg) >= 4.5), None)

def step(p, ink):   # the stair's second plate: one step lighter (or darker) of the same colour, still readable with ink
    L, C, H = lch(p)
    for dL in (0.07, -0.07, 0.04, -0.04):
        q = from_lch(L + dL, C, H)
        if 0 < L + dL < 1 and contrast(ink, q) >= 4.5: return q
    return p

def roles(cols):
    """the brand's colours in its own order (a sheet lists the main one first) -> primary, secondary, light tint, dark"""
    pri = next((c for c in cols if lch(c)[1] >= 0.06), cols[0]); rest = [c for c in cols if c is not pri]
    dark = min((c for c in rest if lch(c)[0] < 0.45), key=lambda c: lch(c)[0], default=None)
    light = max((c for c in rest if lch(c)[0] > 0.8 and lch(c)[1] >= 0.02), key=lambda c: lch(c)[0], default=None)
    sec = next((c for c in rest if c is not dark and c is not light and lch(c)[1] >= 0.06 and hue_gap(c, pri) > 30), None)
    return pri, sec, light, dark

def highlight_from(sec):
    """the highlighted word: coloured text with a black outline, so it must stay far from black (8:1) and visibly coloured."""
    if sec is None or lch(sec)[1] < 0.06: return None
    L, C, H = lch(sec); h = sec
    while contrast(INK, h) < 8 and L < 0.97: L += 0.01; h = from_lch(L, C, H)
    return h

def dominant(img, screenshot=False, k=6):
    if screenshot: k = 10   # a page mixes photos, text and the brand's own bands: more clusters, and chroma counts twice
    """brand colours: k-means in OKLab on the opaque pixels, ranked by share x chroma. White, black and greys never count;
    dark saturated colours (navy, maroon) do; in a screenshot, skin doesn't. Up to 2, at least 45 degrees of hue apart."""
    im = img.convert("RGBA"); im.thumbnail((96, 96))
    a = np.asarray(im, float) / 255; px = a[..., :3][a[..., 3] > 0.5]
    if len(px) < 20: return []
    lab = oklab(px); cent = lab[np.random.default_rng(0).choice(len(lab), min(k, len(lab)), replace=False)]
    for _ in range(12):
        lbl = ((lab[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        cent = np.array([lab[lbl == i].mean(0) if (lbl == i).any() else cent[i] for i in range(len(cent))])
    out = []
    for i, c in enumerate(cent):
        share = (lbl == i).mean(); L, C = c[0], float(np.hypot(c[1], c[2])); H = float(np.degrees(np.arctan2(c[2], c[1])) % 360)
        if share < 0.02: continue
        if screenshot and 0.55 < L < 0.88 and 0.03 < C < 0.13 and 25 < H < 85: continue
        dark = L < 0.45 and C >= 0.025
        if C < 0.04 and not dark: continue
        w = share * C * C * 10 if screenshot else share * (C + (0.08 if dark else 0.02))   # a page: the loudest colour, not the most pixels
        out.append((w, np.clip(from_oklab(c), 0, 1)))
    out.sort(key=lambda x: -x[0])
    if not out: return []
    first = out[0][1]; second = next((o[1] for o in out[1:] if hue_gap(o[1], first) > 45), None)
    return [first] + ([second] if second is not None else [])

# ---------- logo ----------
def prep_logo(path, notes):
    """-> (RGBA logo, trimmed, transparent where it should be; 'mark' | 'tile'; the flat background colour or None)"""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    al = np.asarray(im)[..., 3]
    if (np.concatenate([al[0], al[-1], al[:, 0], al[:, -1]]) < 250).mean() >= 0.5:   # already transparent around it
        return im.crop(im.getbbox() or (0, 0, *im.size)), "mark", None
    rgb = im.convert("RGB"); a = np.asarray(rgb, float)
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]); med = np.median(edge, 0)
    if (np.abs(edge - med).sum(1) < 40).mean() > 0.85:   # a flat colour around it: take it away from the corners inwards
        W, H = rgb.size; key = (255, 0, 254)
        for xy in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]: ImageDraw.floodfill(rgb, xy, key, thresh=40)
        hole = (np.asarray(rgb) == key).all(-1)
        if hole.mean() < 0.97:
            # a soft matte, not a hard cut: alpha from the distance to the background colour, the colour un-mixed from it,
            # so anti-aliased edges don't keep a fringe of the old background (11-09: navy outlines on a white end card)
            px = np.asarray(im, float); bgc = med.astype(float)
            dist = np.abs(px[..., :3] - bgc).sum(-1); ink = np.percentile(dist[~hole], 90) if (~hole).any() else 150
            al = np.where(hole, 0, np.clip(dist / max(ink, 60), 0, 1))   # 1 at the logo's own colour, 0 at the background
            rgb = np.where(al[..., None] > 0.01, (px[..., :3] - bgc * (1 - al[..., None])) / np.maximum(al[..., None], 0.01), 0)
            im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8), "RGBA")
            notes.append("ลบพื้นหลังโลโก้ออกให้แล้ว")
            return im.crop(im.getbbox()), "mark", med / 255
    notes.append("โลโก้มีภาพเป็นพื้นหลัง ใช้ทั้งภาพเป็นกรอบมุมมน")
    return rounded(im), "tile", None

def rounded(im):   # the picture as a rounded tile, like an app icon
    im = im.copy(); m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=int(min(im.size) * 0.18), fill=255)
    im.putalpha(m); return im

def ink_of(im):   # the logo's average colour (opaque pixels)
    a = np.asarray(im.convert("RGBA"), float) / 255; px = a[..., :3][a[..., 3] > 0.5]
    return px.mean(0) if len(px) else WHITE

def tinted(im, rgb):   # same shape, one colour
    a = np.asarray(im.convert("RGBA")).copy(); a[..., :3] = (np.asarray(rgb) * 255).astype(np.uint8); return Image.fromarray(a)

# ---------- any file a shop has -> a PNG Pillow reads ----------
def to_png(src, f):
    """iPhone HEIC, SVG, a PDF guide (its first page), GIF, TIFF -> src/.converted/<f>.png (hidden, so never an input and
    never a change the build reacts to); re-made only when the file is newer. macOS only (sips, Quick Look)."""
    p, out = os.path.join(src, f), os.path.join(src, ".converted", f + ".png")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(p): return out
    if sys.platform != "darwin": return None
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        if f.lower().endswith(".svg"):   # ponytail: Quick Look draws it on white; a white-only SVG logo vanishes (ask for a PNG)
            d = tempfile.mkdtemp(); subprocess.run(["qlmanage", "-t", "-s", "1600", "-o", d, p], capture_output=True, timeout=60)
            shutil.move(os.path.join(d, f + ".png"), out)
        else: subprocess.run(["sips", "-s", "format", "png", p, "--out", out], capture_output=True, timeout=60, check=True)
        with Image.open(out) as im: im.load()
        return out
    except Exception: return None

def ocr(path):   # macOS Vision: [{"text", "box": [x, y, w, h] in pixels, top-left origin}]
    if sys.platform != "darwin": return []
    try:
        r = subprocess.run(["osascript", "-l", "JavaScript", os.path.join(SKILL, "scripts", "ocr_text.js"), path], capture_output=True, text=True,
                           timeout=60, env={**os.environ, "OCR_LANGS": "th-TH,en-US"})
        return json.loads(r.stdout.strip().splitlines()[0]).get("lines", [])
    except Exception: return []

HEXRE, TRIPLE = re.compile(r"#\s?([0-9A-Fa-fOo]{6})(?![0-9A-Za-z])"), re.compile(r"(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
def close(a, b): return float(np.linalg.norm(oklab(a) - oklab(b))) < 0.04   # about ΔE 4: the same colour to the eye

def read_sheet(path, lines=None):
    """a brand sheet or style guide (11-10 test: "<Clinic>'s Brand Colors", 3 rows of hex / name / RGB / HSL /
    CMYK): -> {"colors": [{"hex", "name", "checked"}], "name"} when it lists 2+ colour codes, else None. Every code is
    taken, in the sheet's order. Vision reads 0 as O ("#0OCCFF"): fixed. Each code is checked against the swatch it sits
    on (the most common colour in its box) or an RGB triple on its row; when the text disagrees with both, and they agree
    with each other, they win."""
    lines = lines if lines is not None else ocr(path)
    hexes = [(l, m) for l in sorted(lines, key=lambda l: (round(l["box"][1] / 20), l["box"][0])) for m in HEXRE.finditer(l["text"])]
    if len(hexes) < 2: return None
    with Image.open(path) as im: rgb = np.asarray(im.convert("RGB"))
    out, seen = [], set()
    for l, m in hexes:
        h = m.group(1).upper().replace("O", "0"); c = hex2rgb(h); x, y, w, hh = [int(v) for v in l["box"]]
        cy = y + hh / 2; row = sorted((o for o in lines if o is not l and abs(o["box"][1] + o["box"][3] / 2 - cy) < hh * 0.7), key=lambda o: o["box"][0])
        box = rgb[max(0, y):y + hh, max(0, x):x + w].reshape(-1, 3)
        vals, n = np.unique(box // 8, axis=0, return_counts=True); sw = (vals[n.argmax()] * 8 + 4) / 255 if len(box) else None
        if sw is not None and lch(sw)[0] > 0.95 and lch(sw)[1] < 0.02 and not close(sw, c): sw = None   # plain page, no swatch
        trips = [np.array([int(v) for v in t]) / 255 for o in row for t in TRIPLE.findall(o["text"]) if all(int(v) < 256 for v in t)]
        checked = (sw is not None and close(sw, c)) or any(close(t, c) for t in trips)
        if not checked and sw is not None and any(close(t, sw) for t in trips):
            c = next(t for t in trips if close(t, sw)); h = rgb2hex(c)[1:]; checked = True
        name = next((o["text"].strip() for o in row if o["box"][0] > x and re.search(r"[A-Za-zก-๙]{3}", o["text"]) and not re.search(r"\d|#", o["text"])), "")
        if h not in seen: seen.add(h); out.append({"hex": "#" + h, "name": name, "checked": bool(checked)})
    title = next((m.group(1).strip() for l in lines for m in [re.match(r"(.+?)['’]s\s+brand\s+colou?rs?", l["text"], re.I) or re.match(r"สี(?:ของ)?แบรนด์\s+(.+)", l["text"])] if m), None)
    return {"colors": out, "name": title} if len(out) >= 2 else None

# ---------- a page screenshot: its logo and name (11-09 test: one screenshot was all the tester gave) ----------
def from_screenshot(path):
    """-> (logo crop as a temp PNG path, brand name) or (None, None). macOS Vision reads the header band; the logo is the
    text block at the top left (where sites put it): stacked lines merged ("Name / Bangkok / Clinic"), a 1-2 letter
    misread mark in front dropped from the name. A logo with no text in it (a picture-only mark)
    isn't found: the page asks for the logo file instead."""
    if sys.platform != "darwin": return None, None
    im = Image.open(path).convert("RGB"); W, H = im.size; band = im.crop((0, 0, W, int(H * 0.16)))
    tmp = tempfile.mkdtemp(); bp = os.path.join(tmp, "band.png"); band.save(bp); lines = ocr(bp)
    lines = sorted((l for l in lines if l["box"][0] < 0.15 * W and l["text"].strip()), key=lambda l: (l["box"][0], l["box"][1]))
    if not lines: return None, None
    first = lines[0]; block = [first]
    for l in sorted(lines, key=lambda l: l["box"][1]):   # stacked lines under/over it, left edges aligned
        x, y, w, h = l["box"]; X, Y, _, Hh = first["box"]
        if l is not first and abs(x - X) < 1.5 * Hh and any(abs(y - (b["box"][1] + b["box"][3])) < 1.2 * Hh or abs(b["box"][1] - (y + h)) < 1.2 * Hh for b in block):
            block.append(l)
    block.sort(key=lambda l: l["box"][1])
    words = " ".join(l["text"].strip() for l in block).split()
    if len(words) > 1 and len(words[0]) <= 2: words = words[1:]
    name = " ".join(words)
    x0 = min(l["box"][0] for l in block); y0 = min(l["box"][1] for l in block)
    x1 = max(l["box"][0] + l["box"][2] for l in block); y1 = max(l["box"][1] + l["box"][3] for l in block)
    pad = int(0.8 * first["box"][3]) + 2   # Vision's boxes hug the glyphs: room for the last letter and the mark
    crop = band.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(band.height, y1 + pad)))
    cp = os.path.join(tmp, "logo-from-page.png"); crop.save(cp)
    return cp, (name if re.search(r"\w{2}", name) else None)

# ---------- font ----------
def bundled():   # the Thai fonts TadClip ships (library/fonts/thai), by squashed lower-case name
    try: return {k.lower().replace(" ", ""): k for k in json.load(open(os.path.join(THAI_FONTS, "metrics.json")))}
    except Exception: return {}

def has_thai(path):
    """drawn, not read from the mask: Pillow 12's getmask() has no tobytes() (11-10 test: every font file crashed this
    script and the page showed ClubGig). A Thai letter must draw something, and not the font's "missing" box (U+E000)."""
    f = ImageFont.truetype(path, 60)
    def ink(ch): im = Image.new("L", (140, 120)); ImageDraw.Draw(im).text((30, 10), ch, font=f, fill=255); return im.tobytes()
    miss = ink("\ue000")
    return all(any(ink(ch)) and ink(ch) != miss for ch in "\u0e01\u0e02\u0e2d\u0e32\u0e40")

def font_metrics(path):   # advances per 1000 units, the format of library/fonts/thai/metrics.json (popup line breaks)
    f = ImageFont.truetype(path, 1000)
    return {chr(c): round(f.getlength(chr(c))) for c in list(range(0x20, 0x7F)) + list(range(0x0E01, 0x0E5C))}

# ---------- brand.txt: "label: value" lines, Thai or English labels ----------
KEYS = [("primary", r"สีหลัก|primary|main colou?r"), ("secondary", r"สีรอง|secondary|accent"), ("light", r"สีอ่อน|light colou?r|tint"),
        ("dark", r"สีเข้ม|dark colou?r|text colou?r"), ("font", r"ฟอนต์|font"),
        ("name", r"ชื่อ(แบรนด์|ร้าน)?|name|brand"), ("tagline", r"สโลแกน|tagline|slogan"),
        ("linebutton", r"ปุ่ม ?line|line button|line text"), ("line", r"line( id)?|ไลน์"), ("avoid", r"ห้ามใช้|avoid|don'?t use")]
def read_txt(path):
    out = {}
    for raw in open(path, encoding="utf-8-sig"):
        m = re.match(r"\s*([^:=]+?)\s*[:=]\s*(.+?)\s*$", raw)
        if m:
            k = m.group(1).lower()
            key = next((x for x, pat in KEYS if re.fullmatch(pat, k, re.I)), None)
            if key: out.setdefault(key, m.group(2))
    return out

def hexval(v):
    m = re.search(r"#?\b([0-9a-fA-F]{6})\b", v or ""); return hex2rgb(m.group(1)) if m else None

# the same notes in English, for the page in English (the reel's summary uses the Thai)
EN = [(r"ลบพื้นหลังโลโก้ออกให้แล้ว", "Removed the logo's background"),
      (r"โลโก้มีภาพเป็นพื้นหลัง.*", "The logo has a picture behind it: used whole, as a rounded tile"),
      (r"(.+): ไฟล์ SVG ใช้ไม่ได้.*", r"\1: SVG can't be used, save it as PNG"),
      (r"โลโก้สีเข้ม บนวิดีโอ.*", "Dark logo: shown white over the video"),
      (r"ไฟล์โลโก้เล็ก.*", "Small logo file: the end card may look soft, a bigger file is better"),
      (r'อ่านสีหลัก "(.+)" ไม่ออก.*', r'Couldn\'t read the main colour "\1": write it like #1F6FEB'),
      (r"ไม่ได้ระบุสี ใช้สีจากโลโก้", "No colours given: taken from the logo"),
      (r"ไม่ได้ระบุสี ใช้สีจากภาพหน้าเพจ", "No colours given: taken from the page screenshot"),
      (r"โลโก้ไม่มีสี.*", "The logo has no colour: black text plates"),
      (r"สีหลักอ่อน ใช้เป็นสีเน้นคำ.*", "Light main colour: used for the highlighted word, the second colour for the plates"),
      (r"สีหลักอ่อน ตัวหนังสือขาว.*", "Main colour too light for white text: a darker shade of it is used"),
      (r"โลโก้สีอ่อน บนพื้นขาว.*", "Light logo: the end card uses it in the brand's dark colour"),
      (r"สีหลักอ่อน ตัวหนังสือบนสีนี้ใช้สีเข้มของแบรนด์.*", "Light main colour: the text on it is the brand's own dark colour, so the colour stays as it is"),
      (r"สีหลักอ่อน ตัวหนังสือบนสีนี้ใช้สีเข้ม.*", "Light main colour: dark text on it, so the colour stays as it is"),
      (r"อ่านสีแบรนด์จากชีตสี (\d+) สี: (.+)", r"Read \1 brand colours from the colour sheet: \2"),
      (r"(.+): เปิดไฟล์นี้ไม่ได้.*", r"\1: can't open this file, save it as PNG and add it again"),
      (r"(.+): เปิดไฟล์ฟอนต์นี้ไม่ได้", r"\1: can't open this font file"),
      (r"ฟอนต์ (.+) ไม่มีตัวอักษรไทย.*", r"Font \1 has no Thai letters: Kanit is used"),
      (r"ไม่มีฟอนต์ (.+) ในเครื่อง.*", r"Font \1 isn't on this Mac: Kanit is used (put its .ttf file in the folder)"),
      (r"ยังไม่มีโลโก้ ใช้ชื่อแบรนด์แทน", "No logo yet: the brand name is used"),
      (r"ยังไม่มีโลโก้และชื่อแบรนด์.*", "No logo or name yet: the clip ends on the last word, no logo card"),
      (r"ไม่ได้ใส่ LINE ID.*", "No LINE ID: no LINE button in the clip (add it in the LINE ID field on the TadClip page)"),
      (r"อ่านชื่อแบรนด์จากภาพหน้าเพจ: (.+)", r"Brand name read from the page: \1"),
      (r"ตัดโลโก้จากภาพหน้าเพจให้แล้ว.*", "Logo cut from the page screenshot: a real logo file will be sharper"),
      (r"หาโลโก้ในภาพหน้าเพจไม่เจอ.*", "No logo found in the page screenshot: add a logo file")]
def english(n): return next((re.sub(pat, en, n) for pat, en in EN if re.fullmatch(pat, n)), n)

# ---------- the kit ----------
def find_dir(arg):
    return arg or os.path.join(os.environ.get("TADCLIP_DIR") or os.path.expanduser("~/TadClip"), "brand")

def make(src, proj=None):
    """-> the kit (dict), or None when there's nothing to use. Writes into proj/brand/ when proj is given. Every file in the
    folder gets a role or "not used" with a reason (kit["files"], kit["why"]): nothing is dropped without a word."""
    if not os.path.isdir(src): return None
    files = sorted(f for f in os.listdir(src) if not f.startswith("."))
    fonts = [f for f in files if f.lower().endswith(FONT)]
    txt = next((f for f in files if f.lower() in ("brand.txt", "แบรนด์.txt")), None)
    notes, why, t = [], {}, read_txt(os.path.join(src, txt)) if txt else {}
    paths = {f: os.path.join(src, f) for f in files if f.lower().endswith(IMG)}
    for f in files:
        if f.lower().endswith(CONVERT):
            p = to_png(src, f)
            if p: paths[f] = p
            else: why[f] = "เปิดไฟล์นี้ไม่ได้ บันทึกเป็น PNG แล้ววางใหม่"; notes.append(f"{f}: {why[f]}")
    for f in list(paths):   # one damaged picture is that file's problem, not the whole brand's
        try:
            with Image.open(paths[f]) as im: im.verify()
        except Exception: del paths[f]; why[f] = "เปิดไฟล์นี้ไม่ได้ บันทึกเป็น PNG แล้ววางใหม่"; notes.append(f"{f}: {why[f]}")
    imgs = sorted(paths)
    if not (imgs or fonts or txt or why): return None
    named = [f for f in imgs if re.search(r"logo|โลโก้", f, re.I)]
    dark = next((f for f in imgs if re.search(r"dark|เข้ม", f, re.I)), None)
    light = next((f for f in imgs if f != dark and re.search(r"light|white|ขาว", f, re.I)), None)
    def is_shot(f):   # a page screenshot: wide, big, nothing see-through (a macOS screenshot has an alpha channel, all opaque)
        with Image.open(paths[f]) as im: return im.width >= 900 and im.width / im.height > 1.25 and ("A" not in im.getbands() or im.getchannel("A").getextrema()[0] == 255)
    def big(f):
        with Image.open(paths[f]) as im: return max(im.size) >= 500
    others = [f for f in imgs if f not in named and f not in (dark, light)]
    sheets = {f: r for f in others if big(f) for r in [read_sheet(paths[f])] if r}   # a brand sheet / guide: lists colour codes
    shots = [f for f in others if f not in sheets and is_shot(f)]
    logo = next((f for f in named if f not in (dark, light)), None) or next((f for f in others if f not in shots and f not in sheets), None) or light or dark
    sheet = next(iter(sheets.values()), None)
    kit = {"from": src, "name": t.get("name", ""), "notes": notes}
    have = {"logo": "file" if logo else None, "name": "brand.txt" if t.get("name") else None, "colours": None, "font": None}
    if sheet and sheet["name"] and not kit["name"]: kit["name"] = sheet["name"]; have["name"] = "sheet"
    role = ({logo: "logo"} if logo else {}) | ({dark: "logo-dark"} if dark and dark != logo else {}) | ({light: "logo-light"} if light and light != logo else {}) \
        | {f: "sheet" for f in sheets} | {f: "screenshot" for f in shots[:1]} | ({txt: "brand.txt"} if txt else {})
    page_logo = None
    if shots and (not logo or not kit["name"]):   # the screenshot also gives the logo and the name, when it can
        page_logo, page_name = from_screenshot(paths[shots[0]])
        if page_name and not kit["name"]: kit["name"] = page_name; have["name"] = "screenshot"; notes.append(f"อ่านชื่อแบรนด์จากภาพหน้าเพจ: {page_name}")
        if logo: page_logo = None
        elif page_logo:
            have["logo"] = "screenshot"; notes.append("ตัดโลโก้จากภาพหน้าเพจให้แล้ว ใส่ไฟล์โลโก้จริงจะคมกว่า")
            try: shutil.copy(page_logo, os.path.join(src, ".logo-from-page.png"))   # what the page row shows (hidden: never an input)
            except OSError: pass
        else: notes.append("หาโลโก้ในภาพหน้าเพจไม่เจอ ใส่ไฟล์โลโก้ได้")
    out = os.path.join(proj, "brand") if proj else None
    if out:
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(out):   # the reel had ClubGig's brand (or an older kit) here: one brand per reel
            if f.startswith(("clubgig-", "own-")): os.remove(os.path.join(out, f))

    lg = card = video = None
    if logo or page_logo:   # one version for over the footage, one for the white end card
        lg, kind, bg = prep_logo(paths[logo] if logo else page_logo, notes)
        ink = ink_of(lg)
        if light and light != logo: video = prep_logo(paths[light], [])[0]
        else:
            video = lg if kind == "tile" or lum(ink) > 0.12 else tinted(lg, WHITE)
            if video is not lg: notes.append("โลโก้สีเข้ม บนวิดีโอใช้เป็นสีขาว")
        if dark and dark != logo: card = prep_logo(paths[dark], [])[0]
        elif bg is not None and logo:   # a profile picture: on the white end card the picture as it was reads best (11-09 McDelivery test)
            card = rounded(ImageOps.exif_transpose(Image.open(paths[logo])).convert("RGBA"))
        elif kind == "tile" or contrast(ink, WHITE) >= 1.6: card = lg
        ar = lg.width / lg.height
        if max(lg.size) < 300: notes.append("ไฟล์โลโก้เล็ก ตอนจบอาจไม่คม มีไฟล์ใหญ่กว่านี้ใส่แทนได้")
        kit["logo"] = {"file": (os.path.relpath(paths[logo], src) if logo else ".logo-from-page.png"), "from": "file" if logo else "screenshot",
                       "shape": "wide" if ar > 2.5 else "square" if ar < 1.4 else "box", "bg": rgb2hex(bg) if bg is not None else None}

    # colours: typed (brand.txt / the page's fields), else every code on a brand sheet, else the logo (a profile picture's
    # flat background first: that IS their colour), else the screenshot
    pri, sec, lt, dk = [hexval(t.get(k)) for k in ("primary", "secondary", "light", "dark")]
    if t.get("primary") and pri is None: notes.append(f"อ่านสีหลัก \"{t['primary']}\" ไม่ออก ใช้รหัสสีแบบ #1F6FEB")
    listed = [{"hex": rgb2hex(c), "name": ""} for c in (pri, sec, lt, dk) if c is not None]
    if pri is not None: have["colours"] = "brand.txt"
    elif sheet:
        pri, sec, lt, dk = roles([hex2rgb(c["hex"]) for c in sheet["colors"]]); have["colours"] = "sheet"; listed = sheet["colors"]
        notes.append(f"อ่านสีแบรนด์จากชีตสี {len(listed)} สี: " + " ".join(c["hex"] for c in listed))
    else:
        found = []
        if have["logo"] == "screenshot":   # the logo was cut from the page: the page's own loudest colour is the brand's
            with Image.open(paths[shots[0]]) as im: found = dominant(im, screenshot=True)
        if kit.get("logo", {}).get("bg") and have["logo"] == "file": found.append(hex2rgb(kit["logo"]["bg"]))
        if lg is not None: found += dominant(lg)
        if not found and shots:
            with Image.open(paths[shots[0]]) as im: found = dominant(im, screenshot=True)
        found = [c for c in found if lch(c)[1] >= 0.025 or lch(c)[0] < 0.45]   # a white logo isn't a colour
        if found:
            pri = found[0]; notes.append("ไม่ได้ระบุสี ใช้สีจากโลโก้" if have["logo"] == "file" else "ไม่ได้ระบุสี ใช้สีจากภาพหน้าเพจ")
            have["colours"] = "logo" if have["logo"] == "file" else "screenshot"
            sec = next((c for c in found if hue_gap(c, pri) > 30), None); listed = [{"hex": rgb2hex(c), "name": ""} for c in [pri, sec] if c is not None]
    if pri is None and lg is not None:   # a black-and-white logo: black plates, the style's highlight
        pri = hex2rgb("#1A1A1A"); notes.append("โลโก้ไม่มีสี ใช้แผ่นข้อความสีดำ")
    if pri is not None and sec is not None and dk is None and contrast(WHITE, pri) < 3 and contrast(WHITE, sec) >= 3 and lch(sec)[1] >= 0.06:
        pri, sec = sec, pri   # a light main colour and no dark of their own (a yellow + red brand): red plates, yellow word
        notes.append("สีหลักอ่อน ใช้เป็นสีเน้นคำ และใช้สีรองเป็นแผ่นข้อความ")
    if pri is not None:
        ink = ink_for(pri, dk); p = pri
        if ink is None: p = plate_from(pri)[0]; ink = WHITE; notes.append("สีหลักอ่อน ตัวหนังสือขาวบนสีนี้อ่านยาก ใช้สีเดียวกันที่เข้มขึ้นให้แล้ว")
        elif contrast(ink, WHITE) > 1.01: notes.append("สีหลักอ่อน ตัวหนังสือบนสีนี้ใช้สีเข้ม" + ("ของแบรนด์" if dk is not None and ink is dk else "") + " สีแบรนด์จึงไม่เปลี่ยน")
        p2 = lt if lt is not None and not close(lt, p) and ink_for(lt, dk) is not None else step(p, ink)
        ink2 = ink_for(p2, dk); ink2 = ink if ink2 is None else ink2
        # the highlighted word (coloured, black outline, >= 8:1): their second colour, else the main one, else the tint, as
        # long as it barely needs lightening; else ClubGig's yellow
        hl = next((h for c in (sec, pri, lt) if c is not None for h in [highlight_from(c)] if h is not None and abs(lch(h)[0] - lch(c)[0]) <= 0.12), None)
        hl = hl if hl is not None else hex2rgb(YELLOW)
        bub = dk if dk is not None else p; bink = ink_for(bub, dk); bink = WHITE if bink is None else bink
        H = lambda c: rgb2hex(c) if c is not None else None
        kit["colors"] = {"primary": H(pri), "secondary": H(sec), "light": H(lt), "dark": H(dk), "list": listed}
        kit["impact"] = {"plate": H(p), "plate2": H(p2), "block": H(p), "color": H(hl), "ink": H(ink), "ink2": H(ink2), "blockInk": H(ink)}
        kit["brand"] = {"accent": H(p), "bubble": H(bub), "bubbleInk": H(bink), "highlight": H(hl), "frame": H(pri), "dark": H(dk if dk is not None else p),
                       # the motion scenes: accent gradients, text on light scenes, kinetic grounds
                       "accentDark": H(dk if dk is not None else from_lch(max(0.2, lch(p)[0] - 0.12), lch(p)[1], lch(p)[2])), "ink": H(dk if dk is not None else INK),
                       "kineticBg": H(lt if lt is not None else pri)}
        # the style's transition (yellow / orange / cyan / blue / orange) in their colours
        kit["swipe"] = [H(c) for c in (pri, sec if sec is not None else dk if dk is not None else p2, lt if lt is not None else p2, pri, dk if dk is not None else p, sec if sec is not None else pri)]
        kit["contrast"] = {"plate": round(contrast(ink, p), 2), "plate2": round(contrast(ink2, p2), 2), "highlight": round(contrast(INK, hl), 2)}
    if lg is not None and card is None:   # too light for the white end card: the same shape in the brand's dark colour
        card = tinted(lg, dk if dk is not None else hex2rgb(kit["impact"]["plate"]) if pri is not None and contrast(hex2rgb(kit["impact"]["plate"]), WHITE) >= 3 else INK)
        notes.append("โลโก้สีอ่อน บนพื้นขาวตอนจบใช้สีเข้มของแบรนด์แทน")

    fam, bundled_fonts = None, bundled()   # font: a file they dropped (the first with Thai), a name they gave, else the style's
    for ff in fonts:
        try: thai = has_thai(os.path.join(src, ff))
        except Exception: why[ff] = "เปิดไฟล์ฟอนต์นี้ไม่ได้"; notes.append(f"{ff}: {why[ff]}"); continue
        if not thai: why[ff] = "ไม่มีตัวอักษรไทย"; notes.append(f"ฟอนต์ {ff} ไม่มีตัวอักษรไทย ใช้ Kanit แทน"); continue
        if fam: why[ff] = "ใช้ฟอนต์ไฟล์แรกแล้ว"; continue
        fam = "Brandfont"; role[ff] = "font"; kit["font_name"] = ImageFont.truetype(os.path.join(src, ff), 20).getname()[0]; have["font"] = "file"
        if out:
            fd = os.path.join(proj, "assets", "fonts"); os.makedirs(fd, exist_ok=True)
            shutil.copy(os.path.join(src, ff), os.path.join(fd, "brandfont-thai." + ff.rsplit(".", 1)[1].lower()))
            json.dump({"Brandfont": font_metrics(os.path.join(src, ff))}, open(os.path.join(out, "own-metrics.json"), "w"))
    if not fam and t.get("font"):
        fam = bundled_fonts.get(t["font"].lower().replace(" ", ""))
        if fam: have["font"] = "brand.txt"; kit["font_name"] = fam
        else: notes.append(f"ไม่มีฟอนต์ {t['font']} ในเครื่อง ใช้ Kanit แทน (วางไฟล์ฟอนต์ .ttf ไว้ในโฟลเดอร์ได้)")
    if fam: kit.setdefault("brand", {})["font"] = fam; kit["font"] = fam

    left = re.sub(r"\s*/\s*", "\n", t.get("tagline", ""))
    if lg is not None:
        shape = kit["logo"]["shape"]
        kit["chrome"] = {"logo": "brand/own-logo-video.png", "logoW": {"wide": 240, "box": 170, "square": 110}[shape], "left": left}
        kit["endcard"] = {"logo": "brand/own-logo-card.png", "logoW": {"wide": 760, "box": 560, "square": 420}[shape]}
    else:
        kit["chrome"] = {"logo": None, "right": kit["name"], "left": left}
        kit["endcard"] = {"logo": None, "title": kit["name"]} if kit["name"] else None   # nothing to show: no end card
        notes.append("ยังไม่มีโลโก้ ใช้ชื่อแบรนด์แทน" if kit["name"] else "ยังไม่มีโลโก้และชื่อแบรนด์ คลิปจะจบที่คำสุดท้าย ไม่มีหน้าโลโก้")
    kit["linecta"] = None   # no LINE ID: no LINE button (never another brand's handle)
    if t.get("line"): kit["linecta"] = {"handle": t["line"] if t["line"].startswith("@") else "@" + t["line"]}
    elif lg is not None or t: notes.append("ไม่ได้ใส่ LINE ID ในคลิปจะไม่มีปุ่ม LINE (ใส่ได้ที่ช่อง LINE ID ในหน้า TadClip)")
    if t.get("linebutton") and kit["linecta"]: kit["linecta"]["lines"] = [x.strip() for x in t["linebutton"].split("/") if x.strip()][:2]
    if t.get("tagline"): kit["tagline"] = t["tagline"]
    if t.get("avoid"): kit["avoid"] = t["avoid"]
    kit["have"] = have
    kit["files"] = {f: role.get(f, "not used") for f in files if not f.endswith(".txt") or f == txt}
    kit["why"] = {f: why.get(f, "มีไฟล์อื่นทำหน้าที่นี้แล้ว") for f, r in kit["files"].items() if r == "not used"}
    kit["notes_en"] = [english(n) for n in notes]
    kit["typed"] = t   # what brand.txt says, for the page's fields
    if lg is not None and not out:   # --show: the page's proof shows the two logos as the reel will (hidden: never an input)
        os.makedirs(os.path.join(src, ".converted"), exist_ok=True)
        video.save(os.path.join(src, ".converted", "proof-video.png")); card.save(os.path.join(src, ".converted", "proof-card.png"))
        kit["proof"] = {"video": ".converted/proof-video.png", "card": ".converted/proof-card.png"}
    if out:
        if lg is not None: video.save(os.path.join(out, "own-logo-video.png")); card.save(os.path.join(out, "own-logo-card.png"))
        json.dump(kit, open(os.path.join(out, "own.json"), "w"), ensure_ascii=False, indent=1)
    return kit

# ---------- self-test: python3 own_brand.py --check ----------
def check():
    import tempfile
    d = tempfile.mkdtemp(); ok = True
    def mark(fg, bg=(0, 0, 0, 0), size=(600, 300)):
        im = Image.new("RGBA", size, bg); ImageDraw.Draw(im).ellipse([size[0] // 4, size[1] // 6, size[0] * 3 // 4, size[1] * 5 // 6], fill=fg); return im
    cases = [
        ("light cyan logo, transparent", {"logo.png": mark((0, 195, 244, 255))}),
        ("white mark on a flat red square (a profile picture)", {"profile.jpg": mark((255, 255, 255, 255), (230, 30, 40, 255), (500, 500)).convert("RGB")}),
        ("white logo + brand.txt in Thai", {"logo.png": mark((255, 255, 255, 255)),
            "brand.txt": "สีหลัก: #FFC72C\nสีรอง: #DB0007\nฟอนต์: Prompt\nLINE: mybrand\nปุ่ม LINE: สนใจคอร์ส / ปรึกษาฟรี\nสโลแกน: A / B"}),
        ("page screenshot only", {"page.jpg": Image.new("RGB", (1280, 800), (20, 30, 120))}),
    ]
    for i, (name, files) in enumerate(cases):
        src, proj = os.path.join(d, f"b{i}"), os.path.join(d, f"p{i}"); os.makedirs(src); os.makedirs(proj)
        for f, v in files.items():
            open(os.path.join(src, f), "w").write(v) if isinstance(v, str) else v.save(os.path.join(src, f))
        k = make(src, proj); c = k.get("contrast", {}); B = os.path.join(proj, "brand")
        good = c.get("plate", 0) >= 4.5 and c.get("plate2", 0) >= 4.5 and c.get("highlight", 0) >= 8
        if "logo" in k: good &= all(os.path.exists(os.path.join(B, f)) for f in ("own-logo-video.png", "own-logo-card.png"))
        if i == 1: good &= "ลบพื้นหลังโลโก้ออกให้แล้ว" in k["notes"] and hue_gap(hex2rgb(k["colors"]["primary"]), hex2rgb("#E61E28")) < 10
        if i == 2:
            good &= k.get("font") == "Prompt" and k["linecta"] == {"handle": "@mybrand", "lines": ["สนใจคอร์ส", "ปรึกษาฟรี"]} and k["chrome"]["left"] == "A\nB"
            good &= contrast(ink_of(Image.open(os.path.join(B, "own-logo-card.png"))), WHITE) > 3   # white logo goes dark on the card
            good &= hue_gap(hex2rgb(k["impact"]["plate"]), hex2rgb("#DB0007")) < 10   # yellow + red: red plates, not mustard
        if i == 1: good &= Image.open(os.path.join(B, "own-logo-card.png")).getpixel((250, 20))[:3] == (230, 30, 40)   # card = the picture
        if i == 3: good &= k["chrome"]["logo"] is None and k["endcard"] is None and k["colors"]["primary"] is not None
        print("ok  " if good else "FAIL", name, json.dumps({"colors": k.get("colors"), "contrast": c, "notes": k["notes"]}, ensure_ascii=False))
        ok &= bool(good)
    # 11-10 test: what a shop really hands over (macOS only: sips, Quick Look, Vision)
    if sys.platform == "darwin":
        def sheet(size=(1600, 800)):   # a brand-colour sheet like the 11-10 tester's: a swatch per row with its code on it, a macOS screenshot (RGBA, opaque)
            im = Image.new("RGBA", size, (255, 255, 255, 255)); dr = ImageDraw.Draw(im); f = ImageFont.load_default(size=44)
            dr.text((40, 30), "Test Clinic's Brand Colors", fill=(20, 20, 20), font=f)
            for i, (h, nm) in enumerate([("#00CCFF", "Cyan"), ("#A0ECFF", "Anakiwa"), ("#344054", "Oxford Blue")]):
                y = 160 + i * 200; dr.rounded_rectangle([40, y, 440, y + 120], 16, fill=h)
                dr.text((110, y + 36), h, fill=(255, 255, 255) if i != 1 else (30, 30, 30), font=f); dr.text((520, y + 36), nm, fill=(20, 20, 20), font=f)
            return im
        def run(name, files, test):
            nonlocal ok
            src, proj = tempfile.mkdtemp(dir=d), tempfile.mkdtemp(dir=d)
            for f, v in files.items():
                p = os.path.join(src, f)
                if callable(v): v(p)
                elif isinstance(v, (str, bytes)): open(p, "w" if isinstance(v, str) else "wb").write(v)
                else: v.save(p)
            try: k = make(src, proj); good = bool(test(k))
            except Exception as e: k, good = {"error": repr(e)}, False
            print("ok  " if good else "FAIL", name, json.dumps({x: k.get(x) for x in ("colors", "font", "files", "why", "error") if x in k}, ensure_ascii=False)[:400])
            ok &= good
        def via(fmt, im):   # save as PNG, then let sips write the format a shop would have
            def w(p): t = p + ".png"; im.save(t); subprocess.run(["sips", "-s", "format", fmt, t, "--out", p], capture_output=True, check=True); os.remove(t)
            return w
        cyan = mark((0, 204, 255, 255))
        run("brand sheet (RGBA screenshot): every code, in order, the cyan kept with their dark text",
            {"logo.png": cyan, "Screenshot 1.png": sheet()},
            lambda k: [c["hex"] for c in k["colors"]["list"]] == ["#00CCFF", "#A0ECFF", "#344054"] and k["impact"]["plate"] == "#00CCFF"
            and k["impact"]["ink"] == "#344054" and k["impact"]["plate2"] == "#A0ECFF" and k["name"] == "Test Clinic" and k["files"]["Screenshot 1.png"] == "sheet")
        run("a PDF guide, an iPhone HEIC logo, an SVG",
            {"guide.pdf": via("pdf", sheet()), "IMG_0001.heic": via("heic", cyan.convert("RGB")),
             "mark.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="#ff0055"/></svg>'},
            lambda k: k["have"]["colours"] == "sheet" and k["files"]["guide.pdf"] == "sheet" and k["files"]["IMG_0001.heic"] == "logo" and "mark.svg" in k["files"])
        thai = "/System/Library/Fonts/Supplemental/Ayuthaya.ttf"; latin = "/System/Library/Fonts/Supplemental/Arial.ttf"
        if os.path.exists(thai) and os.path.exists(latin):
            run("font files: the Thai one used (Pillow 12 crashed here), a Latin one not used with the reason",
                {"logo.png": cyan, "MyFont.ttf": lambda p: shutil.copy(thai, p), "Latin.ttf": lambda p: shutil.copy(latin, p)},
                lambda k: k["font"] == "Brandfont" and k["font_name"] == "Ayuthaya" and k["files"]["MyFont.ttf"] == "font" and k["why"]["Latin.ttf"] == "ไม่มีตัวอักษรไทย")
        run("a file that can't be opened: said, not silently dropped", {"logo.png": cyan, "broken.heic": b"not a picture"},
            lambda k: k["files"]["broken.heic"] == "not used" and "เปิดไฟล์นี้ไม่ได้" in k["why"]["broken.heic"])
    ok &= make(os.path.join(d, "nothing")) is None
    ok &= all(english(n) != n for n in ["ลบพื้นหลังโลโก้ออกให้แล้ว", "ฟอนต์ X.ttf ไม่มีตัวอักษรไทย ใช้ Kanit แทน", 'อ่านสีหลัก "red" ไม่ออก ใช้รหัสสีแบบ #1F6FEB'])
    shutil.rmtree(d); print("all ok" if ok else "FAILED"); return ok

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--check" in a: sys.exit(0 if check() else 1)
    frm = a[a.index("--from") + 1] if "--from" in a else None
    src = find_dir(frm)
    if "--show" in a: print(json.dumps(make(src), ensure_ascii=False)); sys.exit(0)
    proj = next((x for x in a if not x.startswith("--") and x != frm), None)
    if not proj: sys.exit(__doc__)
    k = make(src, os.path.abspath(proj))
    if not k: print(f"no brand kit in {src}: the style's own brand stays"); sys.exit(0)
    print(f"own brand from {src}: " + json.dumps({"colours": [c["hex"] for c in k.get("colors", {}).get("list", [])], "plate": k.get("impact", {}).get("plate"),
                                               "text": k.get("impact", {}).get("ink"), "font": k.get("font_name"), "contrast": k.get("contrast")}, ensure_ascii=False))
    for n in k["notes"]: print("  " + n)
