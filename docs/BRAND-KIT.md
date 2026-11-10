# Brand kit: the user's own brand on every reel

Status: built in `scripts/own_brand.py` (+ `build.mjs`, a brand panel on the app page), 2026-11-09; intake and fidelity
rebuilt after the 11-10 test (docs/TEST-1110.md). Not to be
confused with `scripts/brand_kit.py`, which pulls the brand of a *product a reel talks about* into `brand/kit.json`.

## 1. Why this, first (the evidence)

**What we looked at.** Kitti itself (`/Applications/kitti.app` 0.1.9, static reading only; Codex's REA evidence of
2026-10-25: `ui-observations.md`, the inventory, the embedded SQL), our only real new-user test (11-09 logs), and the
first-run of Canva's Brand Kit and CapCut's brand assets.

**Kitti's first run** (observed): welcome → an activation code from a purchase email → (blocked there in the audit).
Behind it: a 923 MB signed Tauri app with its own ffmpeg, whisper, OCR and VAD binaries, a bundled Node + Chromium video
runtime, a project registry, a render queue and an AI-job table: a full editor. Its own skills treat "the brand kit"
(`kitti/brand.json`: colours, fonts, logo) as *brand truth* that every design starts from.

**Canva / CapCut:** the brand kit is the same three things: logos, colours (primary, secondary), fonts, plus Canva's
brand voice; Canva's Brand Kit Builder can fill it from a website. The fields are typed in a settings screen.

**Our 11-09 test, end to end:** install 11:15 → 11:23 (8 min, no failures) → five failed starts on sign-in
(11:27-11:28; fixed in PR #16) → the first preview at 12:04 (30 min, $2.17). The preview was good, and **it carried
ClubGig's logo, ClubGig's tagline and the LINE button `@CLUBGIG`** (the editor: "no profile.json, so the reel uses the
Clubgig brand"). Nobody but ClubGig can post that reel.

**The one step that widens the market:** *a reel that is theirs without any work.* Every other step already works
for a first-time user (one line to install, one button to cut, OK to finish); the brand is the step where today the
answer is "you can't post this". So: yes, the brand kit, and in the shape a Thai shop already has: not hex codes and
SVGs, but **a LINE or Facebook profile picture, or one screenshot of their page.**

**Lean, like Kitti is not:** no new screen, no settings form, no account. A folder (`~/TadClip/brand/`) they can open
from the page, one row on the page that shows what TadClip picked up, and fixes made for them instead of questions.

**What stops someone with no editing skill**, in order: (1) getting to a first result at all (install, sign-in: done);
(2) not knowing what to ask for (ClubGig as the default, "เริ่มจากศูนย์", the change chips: done); (3) a result that
isn't theirs (this); (4) not knowing what's wrong with it (the summary's last line: what to check before posting).
**The fewest things they ever provide:** the clip, and once, their logo. Everything else is optional words.

## 2. What they do

On the page (step 2), "แก้แบรนด์" opens the brand panel: a drop slot per asset (logo, white logo, dark logo, colour sheet
or brand guide, font; each named by its role, the last one replaced), fields for name, four colours, font, tagline, LINE
ID, LINE button and avoid-list (saved as `brand.txt`), a proof of the reel's own template in their colours and font
(popup stair, highlighted word, logo over the video, end card), every file with its role or "not used" and why, and the
brand library (`~/TadClip/brands/<name>/`: save this brand, use a saved one, or none = ClubGig; using one first saves the
brand in use, so nothing is lost; a team shares a brand by copying its folder). The folder still works by hand:

```
~/TadClip/brand/            (made by the app, with a Thai note "วางโลโก้ที่นี่.txt")
  any picture               the logo: PNG, JPG, WebP, iPhone HEIC, SVG, PDF, GIF, TIFF (converted with sips / Quick Look
                            into brand/.converted, hidden); a LINE / Facebook profile picture
  a colour sheet / guide    an image or PDF that lists colour codes (#00CCFF): every code is read (macOS Vision, the 0/O
                            misread fixed), checked against its swatch or an RGB triple on its row, in the sheet's order;
                            "X's Brand Colors" gives the name
  a page screenshot         optional: wide, no transparency; used for the colour when there's no logo
  brand.txt                 optional, Thai or English labels, every line optional:
                              ชื่อ: ร้านของฉัน       สีหลัก: #1F6FEB      สีรอง: #F5B700     ฟอนต์: Prompt
                              สโลแกน: อร่อย / ทุกวัน   LINE: @myshop        ปุ่ม LINE: สั่งเลย / สอบถาม
                              ห้ามใช้: ภาพเด็ก
  a .ttf / .otf             optional: their own font (must have Thai)
  logo-dark.png             optional: the version for the white end card
  logo-white.png            optional: the version over the video (also "light", "ขาว")
```

Which brand wins: `~/TadClip/brand/` → `profile.json` `brand` → ClubGig. (A per-clip override was left out: no one has
asked for two brands.)

## 3. Where each item goes in a ClubGig reel

| Slot in the reel | From | Fill-in rule |
|---|---|---|
| Popup plate (the stair), question-card block | main colour, **as it is** | the text on it is white, else the brand's own dark colour, else near-black: the first at WCAG ≥ 4.5:1. Only when none passes (a mid-tone) is the plate darkened (11-10 test: a light cyan had been darkened to teal for white text; the brand's own navy on it is 5.5:1) |
| Second stair step | light colour | the brand's light tint with its readable text colour; none → one step lighter or darker of the plate |
| Highlighted word (coloured text, black outline) | second colour, else main, else light | ≥ 8:1 against the outline, taken only if that needs ≤ 0.12 lightness; else ClubGig yellow |
| LINE bubble | dark colour, else the plate | its readable text colour |
| The style's transition (swipe), photo-panel frame, small labels, motion-scene accents | palette | main → second/dark gradient, light brush, dark field, main iris; the ClubGig yellow/orange are gone |
| Logo top right, over the footage | logo | dark logo (luminance < 0.12) → white version |
| Logo on the white end card | logo / logo-dark | too light (< 1.6:1 on white) → the same shape in the plate colour; a profile picture → the picture itself, as a rounded tile |
| Typeface of every text | font | a file with Thai → measured for line breaks; a name → one of the 17 bundled Thai fonts; else Kanit |
| Tagline top left, LINE button | brand.txt | no LINE ID → no LINE button (never another brand's handle) |
| End card | logo, else name | neither → no end card: the reel ends on the last word |

**Colour when none is typed:** a colour sheet first (every code; roles: main = the first saturated one, dark = the
darkest under L 0.45, light = the lightest tint, second = another saturated hue 30°+ away), then a profile picture's flat background first (it *is* their colour), then k-means in OKLab
over the logo's pixels (ranked by share × chroma; white, black and greys never count; navy and maroon do), then the
screenshot (ranked by chroma², skin excluded). A light main colour with a usable second (a yellow + red brand)
swaps roles: red plates, yellow highlight. A logo with no colour at all → black plates.

**Logo prep:** transparent → trimmed. Opaque with one flat border colour → that colour is flood-filled away from the
corners (a profile picture becomes a clean mark). Anything else (a photo behind it) → used whole, as a rounded tile.
SVG → a Thai line asking for a PNG. A file under 300 px → a note that the end card may be soft.

**Nothing is refused.** Every fix is one plain Thai line ("สีหลักอ่อน ... ใช้สีเดียวกันที่เข้มขึ้นให้แล้ว"), shown on the
page under "TadClip ปรับให้" and repeated in the reel's summary.

## 4. The pieces

- `scripts/own_brand.py <project>`: writes `$P/brand/own.json`, `own-logo-video.png`, `own-logo-card.png`,
  `own-metrics.json` (own font); `--show` prints the summary for the page; `--check` is the self-test. Pillow + numpy only.
- `build.mjs` owns the kit: it re-makes `own.json` from the folder whenever the folder changes, and when `own.json` was
  edited by hand or made from another folder (a sha in `own.key`): a build warning says so. A loader failure is a build
  warning too (never a silent ClubGig), and the page shows it in one line.
- `build.mjs`: reads `brand/own.json` over the style (impact, brand, chrome, endcard/linecta beats, `omit`, outro);
  own font face (`.ttf`/`.otf`) and metrics; question-card block and LINE bubble follow the brand.
- `recipes/clubgig/README.md` step 3 runs it first; SKILL.md points "ใส่แบรนด์" at the folder.
- The app: the folder and its note are created on start; step 2 shows one row: logo, a popup sample in their plate,
  highlight and font, "เปลี่ยนแบรนด์" (opens the folder in Finder), and the notes. No brand: "แบรนด์: ClubGig ·
  ใส่แบรนด์ของคุณ". The app's own colours stay ClubGig.

## 5. How it was tested

`own_brand.py --check` (4 made-up brands: light cyan, a profile picture, a white logo + Thai brand.txt, a screenshot
only). Then 3 real brands × 3 ways (full kit, one picture, one screenshot) on our own KG02 ClubGig reel; material,
sources and results kept in a private test folder outside the repo (never exported or posted).

## 6. Later, only if asked

From a website URL (`brand_kit.py pull` already reads a site); a square-mark slot; the brand's own way of breaking the
contrast rule (a site that puts white text on its light colour at 1.9:1: TadClip keeps 4.5:1 and uses their dark text); a font file
per weight; PDF guides past page 1; the app re-tinted to the brand; Canva-style brand voice.
