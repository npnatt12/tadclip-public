// Shared by the three page models: words (Thai first), the API, polling, and the screens every model needs the same way
// (waiting, errors, preview, final). Each model's own HTML decides the flow around them.
export const T = {
  th: {
    lang: "EN", langName: "English", listen: "ฟัง", toDark: "โหมดมืด", toLight: "โหมดสว่าง", getClaude: "ดาวน์โหลด Claude", signin: "เข้าสู่ระบบ Claude", brandNone: "แบรนด์: ClubGig", brandAdd: "ใส่แบรนด์ของคุณ", brandChange: "เปลี่ยนแบรนด์", brandSample: "ข้อความ", brandWord: "ของคุณ", brandNotes: "TadClip ปรับให้", have: { logo: "โลโก้", colours: "สี", name: "ชื่อ", font: "ฟอนต์" }, fromPage: "จากภาพหน้าเพจ", wantLogo: "ใส่ไฟล์โลโก้ (PNG พื้นใส) จะคมที่สุด", roles: { logo: "โลโก้", screenshot: "ภาพหน้าเพจ", font: "ฟอนต์", "brand.txt": "ข้อมูลแบรนด์", "not used": "ไม่ได้ใช้" }, signFirst: "เข้าสู่ระบบ Claude ก่อนเริ่ม", wish: "อยากได้แบบไหน พิมพ์บอกได้ (ไม่ใส่ก็ได้)", wishEg: "เช่น ซับตัวใหญ่ ไม่ใส่เพลง", tagline: "ตัดต่อคลิปพูดหน้ากล้องให้อัตโนมัติ",
    start: "ตัดต่อให้หน่อย", drop: "ลากคลิปมาวางตรงนี้", browse: "เลือกคลิปจากเครื่อง", openFolder: "เปิดโฟลเดอร์ TadClip",
    step1: "เลือกคลิป", step2: "เลือกสไตล์", step3: "กดตัดต่อ", inFolder: "คลิปในโฟลเดอร์ TadClip", noFiles: "ยังไม่มีคลิป",
    picked: "เลือกแล้ว", audio: "เสียง/เพลง", recommended: "แนะนำ", moreStyles: "ดูสไตล์อื่น", lessStyles: "ซ่อนสไตล์อื่น",
    uploading: "กำลังคัดลอกคลิป", working: "กำลังตัดต่อ", about: "ใช้เวลาประมาณ 30-60 นาที",
    left: (m) => (m > 1 ? `เหลืออีกประมาณ ${m} นาที` : "ใกล้เสร็จแล้ว"), stepOf: (n, of) => `ขั้นที่ ${n} จาก ${of}`, starting: "กำลังเริ่ม",
    tips: ["ปิดหน้านี้ได้ เสร็จแล้วจะมีเสียงเตือน", "อย่าปิดฝาเครื่อง และเสียบสายชาร์จไว้"],
    slept: "เครื่องหลับไปพักหนึ่ง ตอนนี้ทำต่อแล้ว", stop: "หยุด",
    moreStylesHint: "ทุกแบบใช้ ClubGig เป็นพื้น แล้วเพิ่มลูกเล่นนี้", previewReady: "คลิปตัวอย่างพร้อมแล้ว", whatDone: "TadClip ทำอะไรไปบ้าง", ok: "โอเค ทำไฟล์จริงเลย", change: "อยากแก้ตรงไหน กดได้เลย",
    chips: ["สว่างขึ้น", "ซูมน้อยลง", "เพลงเบาลง", "สั้นลง"], other: "แก้อย่างอื่น", otherHint: "พิมพ์สิ่งที่อยากแก้", send: "ส่ง", wishEgs: ["ซับตัวใหญ่", "ไม่ใส่เพลง", "สั้นลง เหลือ 1 นาที", "เปิดคลิปให้แรงๆ", "ใส่ปุ่ม LINE ตอนท้าย"], help: "ดูวิธีใช้อีกครั้ง",
    finalReady: "ไฟล์จริงเสร็จแล้ว", showFile: "เปิดดูในโฟลเดอร์", another: "ตัดคลิปใหม่",
    batch: (n) => `ตัดแยกทีละคลิป (${n} คลิป)`, batchHint: "ทำต่อกันจนได้ไฟล์จริงทุกคลิป ไม่ต้องกด OK ทีละคลิป อยากแก้คลิปไหนค่อยเปิดทีหลัง",
    queued: (n) => `รอคิวอีก ${n} คลิป`, waitQuota: (hm) => `รอโควตา Claude ถึง ${hm} แล้ว TadClip จะทำต่อเอง`, doneList: "คลิปที่ตัดแล้ว", openJob: "เปิด",
    limitAt: (hm) => `TadClip จะทำต่อเองเวลา ${hm} ไม่ต้องกดอะไร ปิดหน้านี้ได้ งานที่ทำไปแล้วไม่หาย`,
    asks: "TadClip ถามว่า", yes: "ตกลง ทำต่อเลย", retry: "ลองอีกครั้ง", resume: "ทำต่อจากที่ค้างไว้", back: "กลับไปหน้าแรก",
    folderHow: "ใส่คลิปในโฟลเดอร์ TadClip แล้วรอได้เลย", folderAuto: "ไม่ต้องกดอะไร TadClip เริ่มตัดเอง เสร็จแล้วจะมีเสียงเตือน",
    orDrop: "หรือลากคลิปมาวางที่หน้านี้", hello: "สวัสดี ส่งคลิปที่อยากตัดมาได้เลย", willCut: (s) => `จะตัดแบบ ${s} นะ`,
    changeStyle: "เปลี่ยนสไตล์", chosen: (s) => `เลือก ${s}`, previewMsg: "คลิปตัวอย่างมาแล้ว ดูก่อนได้เลย",
    err: {
      no_claude: ["ยังไม่มี Claude ในเครื่องนี้", "ติดตั้งแอป Claude แล้วเปิดหน้านี้ใหม่"],
      signed_out: ["Claude ยังไม่ได้เข้าสู่ระบบ", "กดปุ่มด้านล่าง หน้าต่างเข้าสู่ระบบจะเปิดขึ้น ล็อกอินครั้งเดียว แล้ว TadClip จะเริ่มตัดต่อเอง"],
      no_net: ["ไม่มีอินเทอร์เน็ต", "ต่อ Wi-Fi แล้วกดลองอีกครั้ง"],
      bad_file: ["เปิดไฟล์นี้ไม่ได้", "ใช้คลิปวิดีโอจากมือถือ (.mov หรือ .mp4)"],
      crashed: ["งานหยุดกลางทาง", "กดทำต่อ งานที่ทำไปแล้วไม่หาย"],
      stopped: ["หยุดแล้ว", "กดทำต่อเมื่อพร้อม"],
      limit: ["ใช้ Claude ครบโควตาแล้ว", "รอจนถึงเวลาที่ Claude บอก แล้วกดทำต่อ งานที่ทำไปแล้วไม่หาย"],
      stuck: ["Claude ไม่ยอมเริ่มงาน", "เปิดแอป Claude ให้ขึ้นหน้าแชต แล้วกดลองอีกครั้ง"],
    },
  },
  en: {
    lang: "ไทย", langName: "ภาษาไทย", listen: "Listen", toDark: "Dark mode", toLight: "Light mode", getClaude: "Get Claude", signin: "Sign in to Claude", brandNone: "Brand: ClubGig", brandAdd: "Add your brand", brandChange: "Change brand", brandSample: "Your", brandWord: "text", brandNotes: "What TadClip adjusted", have: { logo: "Logo", colours: "Colours", name: "Name", font: "Font" }, fromPage: "from the page", wantLogo: "A logo file (transparent PNG) looks sharpest", roles: { logo: "logo", screenshot: "page screenshot", font: "font", "brand.txt": "brand details", "not used": "not used" }, signFirst: "Sign in to Claude first", wish: "Anything you want? Type it here (optional)", wishEg: "e.g. big captions, no music", tagline: "Talking-head clips, edited for you",
    start: "Cut it for me", drop: "Drop your clip here", browse: "Choose from this Mac", openFolder: "Open the TadClip folder",
    step1: "Choose a clip", step2: "Choose a style", step3: "Start", inFolder: "Clips in the TadClip folder", noFiles: "No clips yet",
    picked: "Chosen", audio: "Audio", recommended: "Recommended", moreStyles: "More styles", lessStyles: "Fewer styles",
    uploading: "Copying your clip", working: "Editing", about: "Takes about 30-60 minutes",
    left: (m) => (m > 1 ? `About ${m} min left` : "Almost done"), stepOf: (n, of) => `Step ${n} of ${of}`, starting: "Starting",
    tips: ["You can close this page. You'll hear a sound when it's done", "Keep the lid open and the charger in"],
    slept: "The Mac slept for a while. It's working again", stop: "Stop",
    moreStylesHint: "Each one is ClubGig plus this effect", previewReady: "Your preview is ready", whatDone: "What TadClip did", ok: "Looks good, make the final", change: "Want a change? Click one",
    chips: ["Brighter", "Less zoom", "Quieter music", "Shorter"], other: "Something else", otherHint: "Type what to change", send: "Send", wishEgs: ["Big captions", "No music", "Shorter, about 1 minute", "A strong opening", "A LINE button at the end"], help: "Show the tips again",
    finalReady: "Your final file is ready", showFile: "Show in folder", another: "Cut another clip",
    batch: (n) => `Each clip on its own (${n})`, batchHint: "Runs one after another to finished files, no OK for each. Open any of them later to change it",
    queued: (n) => `${n} more in the queue`, waitQuota: (hm) => `Waiting for Claude's usage window until ${hm}. TadClip carries on by itself`, doneList: "Finished clips", openJob: "Open",
    limitAt: (hm) => `TadClip carries on by itself at ${hm}. Nothing to press; you can close this page. Nothing is lost`,
    asks: "TadClip asks", yes: "OK, carry on", retry: "Try again", resume: "Carry on", back: "Back to start",
    folderHow: "Put clips in the TadClip folder, then wait", folderAuto: "Nothing to press. TadClip starts by itself and plays a sound when it's done",
    orDrop: "or drop a clip on this page", hello: "Hi! Send me the clip you want edited", willCut: (s) => `I'll cut it in ${s}`,
    changeStyle: "Change style", chosen: (s) => `${s}, please`, previewMsg: "Here's your preview",
    err: {
      no_claude: ["Claude isn't on this Mac", "Install the Claude app, then open this page again"],
      signed_out: ["Claude isn't signed in", "Press the button below. A sign-in window opens: sign in once, and TadClip starts by itself"],
      no_net: ["No internet", "Connect to Wi-Fi, then press Try again"],
      bad_file: ["This file can't be opened", "Use a video from your phone (.mov or .mp4)"],
      crashed: ["The edit stopped halfway", "Press Carry on. Nothing done so far is lost"],
      stopped: ["Stopped", "Press Carry on when you're ready"],
      limit: ["Claude's usage limit is reached", "Wait until the time Claude gives, then press Carry on. Nothing is lost"],
      stuck: ["Claude didn't start", "Open the Claude app to its chat, then press Try again"],
    },
  },
};
// changes go to Claude in Thai whatever the page language: the editor's words for them are Thai
const CHIP_TH = T.th.chips;

// ClubGig first and chosen. "More styles" = the 18 effects TadClip rendered for the README (docs/media/effects-grid.gif,
// test-videos/effects-grid-th/make.py), each a 4 s loop in ui/styles/<id>.mp4. Picking one asks for ClubGig + that effect.
export const STYLES = [
  { id: "clubgig", name: "ClubGig", th: "ข้อความขึ้นที่ช่วงอก ภาพสต็อกปัดเข้า ปุ่ม LINE ตอนท้าย", en: "Text on the torso, swiped stock, a LINE button at the end" },
  // "start from scratch" (the owner 11-09): the plain cut, then their own words or the changes after the preview add the rest
  { id: "scratch", name: "From scratch", th: "เริ่มจากศูนย์", en: "From scratch", dth: "ตัดช่วงพูดที่ดีที่สุด ตัดช่วงเงียบ ใส่ซับ ไม่มีอย่างอื่น", den: "Best takes, pauses out, captions, nothing else" },
  { id: "route", name: "Route maps", th: "แผนที่เส้นทาง", en: "Route maps" },
  { id: "counter", name: "Live counters", th: "ตัวเลขนับขึ้น", en: "Live counters" },
  { id: "bigword", name: "Big word captions", th: "คำใหญ่เต็มจอ", en: "Big word captions" },
  { id: "stack", name: "Photo stacks", th: "ภาพซ้อนกอง", en: "Photo stacks" },
  { id: "collage", name: "Cut-out collage", th: "คอลลาจตัดแปะ", en: "Cut-out collage" },
  { id: "board", name: "Hand-drawn board", th: "กระดานวาดมือ", en: "Hand-drawn board" },
  { id: "paper", name: "Paper + highlights", th: "กระดาษ + ไฮไลต์", en: "Paper + highlights" },
  { id: "tree", name: "Growing diagrams", th: "แผนภาพค่อยๆ โต", en: "Growing diagrams" },
  { id: "search", name: "Search + reveal", th: "ค้นหา + เผยคำตอบ", en: "Search + reveal" },
  { id: "kinetic", name: "Kinetic type", th: "ตัวอักษรเคลื่อนไหว", en: "Kinetic type" },
  { id: "callout", name: "Screen callouts", th: "ชี้จุดบนหน้าจอ", en: "Screen callouts" },
  { id: "chalk", name: "Chalk writing", th: "เขียนชอล์ก", en: "Chalk writing" },
  { id: "steps", name: "Step numbers", th: "ตัวเลขทีละขั้น", en: "Step numbers" },
  { id: "engrave", name: "Engraving + lens", th: "ภาพแกะลาย + เลนส์", en: "Engraving + lens" },
  { id: "app", name: "Live app demo", th: "เดโมแอปสด", en: "Live app demo" },
  { id: "weeks", name: "Life in weeks", th: "ชีวิตเป็นสัปดาห์", en: "Life in weeks" },
  { id: "product", name: "Product drop", th: "เปิดตัวสินค้า", en: "Product drop" },
  { id: "broll", name: "B-roll + captions", th: "ภาพประกอบ + คำบรรยาย", en: "B-roll + captions" },
];
export const styleName = (x) => (x.id === "clubgig" ? "ClubGig" : lang === "th" ? x.th : x.en);
export const styleAsk = (id) => { const x = STYLES.find((y) => y.id === id); return !x || id === "clubgig" ? "clubgig" : id === "scratch" ? "scratch" : `ClubGig + ${x.th} (${x.en})`; };
// a tile: ClubGig is a still from a real reel; the effects loop (only while on screen; a still if motion is turned down)
export function tile(x) {
  if (x.id === "clubgig") return `<img src="styles/clubgig.jpg" alt="">`;
  if (x.id === "scratch") return `<span class="ph scratch" aria-hidden="true">${icon("scissors")}</span>`;
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  return `<video src="styles/${x.id}.mp4" poster="styles/${x.id}.jpg" muted loop playsinline preload="none" ${still ? "" : "autoplay"} aria-hidden="true"></video>`;
}

export let lang = localStorage.lang || "th";
// light / dark: follows the Mac until they press the button, then their choice sticks (set before the first paint)
const darkNow = () => (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
export function applyTheme() {
  if (localStorage.theme) document.documentElement.dataset.theme = localStorage.theme; else delete document.documentElement.dataset.theme;
  const b = document.querySelector("[data-act=theme]");
  if (b) { b.innerHTML = icon(darkNow() ? "sun" : "moon"); b.setAttribute("aria-label", darkNow() ? T[lang].toLight : T[lang].toDark); }
}
export const t = () => T[lang];
export function setLang(l) {
  lang = localStorage.lang = l; document.documentElement.lang = l;
  const b = document.querySelector("[data-lang]"); if (b) b.setAttribute("aria-label", `${T[l].lang} ${T[l].langName}`);
  applyTheme();   // its spoken name is in the page language too   // spoken name must contain the visible "EN"
}

const H = { "content-type": "application/json" };
export const api = {
  state: () => fetch("/api/state").then((r) => r.json()),
  start: (files, style, wish) => fetch("/api/start", { method: "POST", headers: H, body: JSON.stringify({ files, style, wish }) }).then((r) => r.json()),
  reply: (text) => fetch("/api/reply", { method: "POST", headers: H, body: JSON.stringify({ text }) }),
  retry: () => fetch("/api/retry", { method: "POST", headers: H }),
  queue: (files, style, wish) => fetch("/api/queue", { method: "POST", headers: H, body: JSON.stringify({ files, style, wish }) }).then((r) => r.json()),
  pick: (id) => fetch("/api/pick", { method: "POST", headers: H, body: JSON.stringify({ id }) }),
  signin: () => fetch("/api/signin", { method: "POST", headers: H }),
  openBrand: () => fetch("/api/open?what=brand", { method: "POST", headers: H }),
  stop: () => fetch("/api/stop", { method: "POST", headers: H }),
  fresh: () => fetch("/api/new", { method: "POST", headers: H }),
  open: (what) => fetch("/api/open" + (what ? `?what=${what}` : ""), { method: "POST", headers: H }),
  settings: (s) => fetch("/api/settings", { method: "POST", headers: H, body: JSON.stringify(s) }),
  async upload(files, onProgress, role) {   // dropped or chosen files are copied into the TadClip folder (brand files into brand/)
    const names = [];
    for (const f of files) { onProgress?.(f.name); const r = await fetch(`/api/upload?name=${encodeURIComponent(f.name)}${role ? `&role=${role}` : ""}`, { method: "POST", body: f }); if (r.ok && (await r.json()).to !== "brand") names.push(f.name); }
    return names;
  },
  brandTxt: (fields) => fetch("/api/brandtxt", { method: "POST", headers: H, body: JSON.stringify(fields) }),
  brands: (act, name) => fetch("/api/brands", { method: "POST", headers: H, body: JSON.stringify({ act, name }) }),
};

// one screen per job state; every model shows these the same way
export function screen(s) {
  const j = s.job;
  if (!s.claude) return "error";
  if (!j) return "home";
  return { running: "running", preview: "preview", final: "final", question: "question", error: "error", stopped: "error" }[j.status] || "home";
}
export const errCode = (s) => (!s.claude ? "no_claude" : s.job?.status === "stopped" ? "stopped" : s.job?.error || "crashed");

export const el = (html) => { const d = document.createElement("template"); d.innerHTML = html.trim(); return d.content.firstElementChild; };
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const ICON = {
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  film: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
  scissors: '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
  check: '<path d="m5 12 5 5L20 7"/>', retry: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
  alert: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 17h.01"/>', play: '<path d="m8 5 11 7-11 7z"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  zoom: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4M8 11h6"/>', music: '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  short: '<path d="M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4"/>', pen: '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>', plus: '<path d="M12 5v14M5 12h14"/>', home: '<path d="m3 11 9-8 9 8M5 9v11h14V9"/>',
  speaker: '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>',
  upload: '<path d="M12 16V4M7 9l5-5 5 5M4 20h16"/>', globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
};
export const icon = (n, cls = "i") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICON[n]}</svg>`;
export const CHIP_ICONS = ["sun", "zoom", "music", "short"];

// the real run took 18 min, the 11-08 test 33: ~30 min spread over the 9 steps, never more than what is left by the clock
export const minutesLeft = (j) => Math.max(1, Math.round(Math.min(30 * (1 - (j.step ? j.step.n / j.step.of : 0)), 40 - (Date.now() - j.started) / 60000)));
export function stepText(j) {
  if (!j.step) return t().starting;
  const s = lang === "th" ? j.step.th : j.step.en;
  return /[฀-๿]/.test(s || "") || lang === "en" ? s : "";   // an English-only line is not shown to a Thai reader (the heading already says กำลังตัดต่อ)
}

// --- the shared screens: waiting, error, preview, final, question ---
export function waiting(j, { compact } = {}) {
  const w = t(), pct = Math.max(4, j.step ? Math.round((100 * j.step.n) / j.step.of) : 0);   // never a stuck-looking 0 %
  return `<section class="wait" aria-live="polite">
    <div class="ring" style="--p:${pct}"><span>${pct}%</span></div>
    <h2>${w.working}</h2>
    ${stepText(j) ? `<p class="big">${esc(stepText(j))}</p>` : ""}
    <p class="muted">${j.step?.n ? w.stepOf(j.step.n, j.step.of) + " · " : ""}${w.left(minutesLeft(j))}</p>
    ${j.slept ? `<p class="note">${w.slept}</p>` : ""}
    ${compact ? "" : `<ul class="tips">${w.tips.map((x) => `<li>${x}</li>`).join("")}</ul>`}
    <button class="btn ghost small" data-act="stop">${icon("stop")}<span>${w.stop}</span></button>
  </section>`;
}
// their brand (~/TadClip/brand/), 11-10 test: one row that says what was taken in (name, every colour, font, logos) and
// a panel with a drop slot per asset, the brand.txt fields, a proof in the reel's own template, and saved brands
const BK = {
  th: { edit: "แก้แบรนด์", close: "ปิด", proof: "ในคลิปจะเป็นแบบนี้", popup: "ข้อความ", popup2: "ของแบรนด์", word: "คำเน้น", end: "หน้าจบ",
    fix: "แก้", slots: "ใส่ไฟล์ (ลากมาวาง หรือกดเลือก)", fields: "หรือพิมพ์เอง", save: "บันทึก", saved: "แบรนด์ที่เก็บไว้", use: "ใช้", store: "เก็บแบรนด์นี้ไว้",
    clubgig: "ไม่ใช้แบรนด์ (ClubGig)", folder: "เปิดโฟลเดอร์", err: "อ่านไฟล์แบรนด์ไม่ได้ ใช้แบรนด์ ClubGig ไปก่อน", errTodo: "เอาไฟล์ที่เพิ่งใส่ออก แล้วลองใหม่",
    role: { sheet: "ชีตสีแบรนด์", "logo-light": "โลโก้สีขาว", "logo-dark": "โลโก้สีเข้ม" }, checked: "ตรงกับสีในชีต", files: "ไฟล์ในโฟลเดอร์", unused: "ไม่ได้ใช้", from: { sheet: "จากชีตสี", screenshot: "จากภาพหน้าเพจ", logo: "จากโลโก้", "brand.txt": "พิมพ์เอง", file: "จากไฟล์" },
    slot: { logo: ["โลโก้", "ภาพไหนก็ได้ PNG พื้นใสคมสุด"], "logo-light": ["โลโก้สีขาว", "ใช้บนวิดีโอ (ไม่มีก็ได้)"], "logo-dark": ["โลโก้สีเข้ม", "ใช้หน้าจบพื้นขาว (ไม่มีก็ได้)"],
      sheet: ["ชีตสีแบรนด์ / คู่มือแบรนด์", "ภาพหรือ PDF ที่มีรหัสสี #"], font: ["ฟอนต์", ".ttf .otf ที่มีภาษาไทย"] },
    f: { name: "ชื่อแบรนด์", primary: "สีหลัก", secondary: "สีรอง", light: "สีอ่อน", dark: "สีเข้ม", font: "ชื่อฟอนต์", tagline: "สโลแกน", line: "LINE ID", linebutton: "ปุ่ม LINE", avoid: "ห้ามใช้" } },
  en: { edit: "Edit brand", close: "Close", proof: "In the clip it looks like this", popup: "Your", popup2: "brand text", word: "Highlight", end: "End card",
    fix: "fix", slots: "Add files (drop here or click)", fields: "Or type it", save: "Save", saved: "Saved brands", use: "Use", store: "Save this brand",
    clubgig: "No brand (ClubGig)", folder: "Open folder", err: "Couldn't read the brand files: ClubGig's brand for now", errTodo: "Take out the file you just added and try again",
    role: { sheet: "colour sheet", "logo-light": "white logo", "logo-dark": "dark logo" }, checked: "matches the colour sheet", files: "Files in the folder", unused: "not used", from: { sheet: "from the colour sheet", screenshot: "from the page", logo: "from the logo", "brand.txt": "typed", file: "from the file" },
    slot: { logo: ["Logo", "any picture; a transparent PNG is sharpest"], "logo-light": ["White logo", "over the video (optional)"], "logo-dark": ["Dark logo", "on the white end card (optional)"],
      sheet: ["Colour sheet / brand guide", "a picture or PDF with # colour codes"], font: ["Font", ".ttf .otf with Thai"] },
    f: { name: "Brand name", primary: "Main colour", secondary: "Second colour", light: "Light colour", dark: "Dark colour", font: "Font name", tagline: "Tagline", line: "LINE ID", linebutton: "LINE button", avoid: "Avoid" } },
};
let bkOpen = false;
const ACCEPT = { font: ".ttf,.otf", sheet: "image/*,.pdf,.heic", logo: "image/*,.heic,.svg,.pdf", "logo-light": "image/*,.heic,.svg", "logo-dark": "image/*,.heic,.svg" };
export function brandRow(k, saved = []) {
  const w = t(), b = BK[lang] || BK.th, i = k?.impact || { plate: "#6A2C3B", plate2: "#87203F", color: "#FFE11A", ink: "#fff", ink2: "#fff" };
  const font = k?.font ? `<style>@font-face { font-family: BrandSample; src: url(/brandfont?f=${encodeURIComponent(k.font)}); }</style>` : "", ff = k?.font ? "font-family:BrandSample, Kanit;" : "";
  const dots = (k?.colors?.list || []).map((c) => `<i class="dot" style="background:${esc(c.hex)}" title="${esc(c.hex)} ${esc(c.name || "")}"></i>`).join("");
  const row = !k || k.error
    ? `<span class="muted">${w.brandNone}</span>${k?.error ? `<p class="bkerr" role="alert">${b.err}: ${esc(k.error)}. ${b.errTodo}</p>` : ""}`
    : `${k.logo ? `<img src="${esc(k.logo)}" alt="">` : ""}<b class="bkname">${esc(k.name || "")}</b><span class="dots">${dots}</span>${k.fontName ? `<span class="muted">${esc(k.fontName)}</span>` : ""}
       <ul class="have">${Object.entries(w.have).map(([key, label]) => { const v = k.have?.[key]; return `<li class="${v ? "yes" : "no"}">${v ? "✓" : "✗"} ${label}${v && b.from[v] && v !== "file" ? ` <small>(${b.from[v]})</small>` : ""}</li>`; }).join("")}</ul>
       ${!k.have?.logo || k.have.logo === "screenshot" ? `<p class="want">${w.wantLogo}</p>` : ""}`;
  const head = `<div class="brandrow">${font}${row}<button class="btn ghost small" data-act="bk" aria-expanded="${bkOpen}">${icon("folder")}<span>${bkOpen ? b.close : k ? b.edit : w.brandAdd}</span></button></div>`;
  if (!bkOpen) return head;
  const held = (role) => Object.entries(k?.files || {}).filter(([, r]) => r === role).map(([f]) => f);
  const slots = Object.entries(b.slot).map(([role, [label, hint]]) => { const h = held(role);
    return `<label class="slot${h.length ? " has" : ""}" id="slot-${role}" data-role="${role}"><input type="file" data-role="${role}" accept="${ACCEPT[role]}" hidden>
      <b>${h.length ? "✓" : "+"} ${label}</b><small>${h.length ? esc(h.join(", ")) : hint}</small></label>`; }).join("");
  const ty = k?.typed || {}, cl = k?.colors || {};
  const field = (key) => { const v = ty[key] ?? "", ph = cl[key] || (key === "name" ? k?.name : key === "font" ? k?.fontName : "") || "";
    const colour = ["primary", "secondary", "light", "dark"].includes(key);
    return `<label class="fld" for="f-${key}"><span>${colour ? `<i class="dot" style="background:${esc(v || ph || "transparent")}"></i>` : ""}${b.f[key]}</span><input id="f-${key}" name="${key}" value="${esc(v)}" placeholder="${esc(ph)}" ${colour ? 'pattern="#?[0-9A-Fa-f]{6}" maxlength="7"' : 'maxlength="120"'} autocomplete="off"></label>`; };
  const proof = k && !k.error ? `<div class="proof"><div class="frame" style="${ff}">${k.proof ? `<img class="lv" src="${esc(k.proof.video)}" alt="">` : ""}
      <span class="hook" style="color:${esc(i.color)}">${b.word}</span>
      <span class="pl" style="background:${esc(i.plate)};color:${esc(i.ink || "#fff")}">${b.popup}</span><span class="pl two" style="background:${esc(i.plate2 || i.plate)};color:${esc(i.ink2 || i.ink || "#fff")}">${b.popup2}</span></div>
    <div class="frame end">${k.proof ? `<img src="${esc(k.proof.card)}" alt="">` : `<b>${esc(k.name || "")}</b>`}<small>${b.end}</small></div>
    <ul class="pal">${(cl.list || []).map((c) => `<li><i class="dot" style="background:${esc(c.hex)}"></i> ${esc(c.hex)} ${esc(c.name || "")}${c.checked ? ` <small>✓ ${b.checked}</small>` : ""}</li>`).join("")}
      ${k.fontName ? `<li>${w.have.font}: <span style="${ff}">${esc(k.fontName)} กขค</span></li>` : ""}${k.avoid ? `<li>${b.f.avoid}: ${esc(k.avoid)}</li>` : ""}
      <li class="fixes"><a href="#f-primary">${b.fix} ${w.have.colours}</a> · <a href="#slot-logo">${b.fix} ${w.have.logo}</a> · <a href="#slot-font">${b.fix} ${w.have.font}</a></li></ul></div>` : "";
  const files = Object.entries(k?.files || {}).map(([f, r]) => `${esc(f)} → ${r === "not used" ? `${b.unused}: ${esc(k.why?.[f] || "")}` : w.roles[r] || b.role[r] || esc(r)}`).join("<br>");
  const notes = k && !k.error ? ((lang === "en" && k.notes_en) || k.notes || []).map(esc).join("<br>") : "";
  return head + `<div class="bkpanel">
    ${proof}
    <h3>${b.slots}</h3><div class="slots">${slots}</div>
    <h3>${b.fields}</h3><form class="bkform">${["name", "primary", "secondary", "light", "dark", "font", "tagline", "line", "linebutton", "avoid"].map(field).join("")}
      <button class="btn small primary" type="submit">${b.save}</button></form>
    ${files || notes ? `<details class="said brandnotes" open><summary>${w.brandNotes}</summary><p>${files}${files && notes ? "<br><br>" : ""}${notes}</p></details>` : ""}
    <h3>${b.saved}</h3><div class="lib"><select id="bklib" aria-label="${b.saved}"><option value="">${b.clubgig}</option>${saved.map((n) => `<option${n === k?.name ? " selected" : ""}>${esc(n)}</option>`).join("")}</select>
      <button class="btn ghost small" data-act="bkuse">${b.use}</button>
      ${k && !k.error ? `<input id="bkname" value="${esc(k.name || "")}" maxlength="60" aria-label="${b.store}"><button class="btn ghost small" data-act="bkstore">${b.store}</button>` : ""}
      <button class="btn ghost small" data-act="brand">${b.folder}</button></div></div>`;
}
export function errorScreen(s) {
  const w = t(), code = errCode(s); let [what, todo] = w.err[code] || w.err.crashed;
  if (code === "limit" && s.job?.resumeAt) todo = w.limitAt(hm(s.job.resumeAt));
  const act = code === "no_claude" ? `<a class="btn primary" href="https://claude.ai/download" target="_blank" rel="noopener">${icon("upload")}<span>${w.getClaude}</span></a>`
    : code === "signed_out" ? `<button class="btn primary" data-act="signin">${icon("check")}<span>${w.signin}</span></button>`
    : code === "crashed" || code === "stopped" || code === "limit" ? `<button class="btn primary" data-act="retry">${icon("retry")}<span>${w.resume}</span></button>`
    : code === "bad_file" ? `<button class="btn primary" data-act="fresh">${icon("film")}<span>${w.browse}</span></button>`
    : `<button class="btn primary" data-act="retry">${icon("retry")}<span>${w.retry}</span></button>`;
  return `<section class="err" role="alert">
    <div class="err-icon">${icon("alert")}</div>
    <h2>${what}</h2>
    <p class="big">${todo}</p>
    ${s.job?.bad ? `<p class="muted file">${esc(s.job.bad)}</p>` : ""}
    ${act}
    ${code !== "bad_file" && s.job ? `<button class="btn ghost small" data-act="fresh">${icon("home")}<span>${w.back}</span></button>` : ""}
  </section>`;
}
export function chipsHTML() {
  const w = t();
  return `<div class="chips">${w.chips.map((c, i) => `<button class="chip" data-chip="${i}">${icon(CHIP_ICONS[i])}<span>${c}</span></button>`).join("")}
    <button class="chip" data-act="other">${icon("pen")}<span>${w.other}</span></button></div>
    <form class="other" hidden><label class="sr" for="otherText">${w.otherHint}</label>
      <input id="otherText" name="t" placeholder="${w.otherHint}" autocomplete="off"><button class="btn primary small">${w.send}</button></form>`;
}
export function previewScreen(j) {
  const w = t();
  return `<section class="pv">
    <video class="phone" src="${esc(j.preview)}" controls playsinline preload="metadata"></video>
    <div class="side"><h2>${icon("play")}<span>${w.previewReady}</span></h2>
    <button class="btn primary" data-act="ok">${icon("check")}<span>${w.ok}</span></button>
    <p class="muted">${w.change}</p>
    ${chipsHTML()}
    ${j.result ? `<details class="said"><summary>${w.whatDone}</summary><p>${esc(plain(j.result))}</p></details>` : ""}
  </div></section>`;
}
// the editor's summary without file paths or code marks: a first-timer reads the words, not the plumbing
export const plain = (s) => String(s).replace(/`[^`]*\/[^`]*`/g, "").replace(/`/g, "").replace(/อยู่ที่\s*(?=\s|$)/g, "").replace(/\s+([,.])/g, "$1");
export function finalScreen(j) {
  const w = t();
  return `<section class="pv">
    <video class="phone" src="${esc(j.final)}" controls playsinline preload="metadata"></video>
    <div class="side"><h2>${icon("check")}<span>${w.finalReady}</span></h2>
    <button class="btn primary" data-act="show">${icon("folder")}<span>${w.showFile}</span></button>
    <button class="btn ghost" data-act="fresh">${icon("plus")}<span>${w.another}</span></button>
    ${j.batch ? `<p class="muted">${w.change}</p>${chipsHTML()}` : ""}
    ${j.result ? `<details class="said" open><summary>${w.whatDone}</summary><p>${esc(plain(j.result))}</p></details>` : ""}
  </div></section>`;   // open: the final summary carries what to check before posting (e.g. strangers' faces unchecked)
}
export const hm = (ms) => new Date(ms).toLocaleTimeString(lang === "th" ? "th-TH" : "en-GB", { hour: "2-digit", minute: "2-digit" });
// the batch: what's waiting, why it waits (Claude's usage window), and the finished clips, each one can be opened again
export function queueRow(s) {
  const w = t(), mine = (s.done || []).filter((d) => d.batch && d.id !== s.job?.id);
  if (!s.queue?.length && !mine.length) return "";
  return `<section class="queue" aria-live="polite">
    ${s.queue?.length ? `<p class="big">${w.queued(s.queue.length)}</p>` : ""}
    ${s.waitUntil ? `<p class="note">${w.waitQuota(hm(s.waitUntil))}</p>` : ""}
    ${mine.length ? `<h3>${w.doneList}</h3><ul class="donelist">${mine.map((d) => `<li><span>${d.status === "final" ? icon("check") : icon("alert")} ${esc(d.name)}</span>
      ${s.job?.status === "running" || s.job?.error === "limit" ? "" : `<button class="btn ghost small" data-pick="${esc(d.id)}">${w.openJob}</button>`}</li>`).join("")}</ul>` : ""}
  </section>`;
}
// the header carries their brand once they have one (the app is then theirs: a brand asset, not ClubGig's); ClubGig's
// wordmark only while no brand is set. Models A and B share this header.
const CLUBGIG_HEAD = `<img class="logo-light" src="clubgig-wordmark-black.png" alt="ClubGig"><img class="logo-dark" src="clubgig-wordmark-white.png" alt="ClubGig"><span class="tc">TadClip</span>`;
export function brandHead(s) {
  const h = document.querySelector(".top .brand"); if (!h) return;
  const k = s.brand && !s.brand.error && (s.brand.logo || s.brand.name) ? s.brand : null;
  const html = k ? `${k.logo ? `<img class="own" src="${esc(k.logo)}" alt="${esc(k.name || "")}">` : ""}${k.name ? `<b class="ownname">${esc(k.name)}</b>` : ""}<span class="tc">TadClip</span>` : CLUBGIG_HEAD;
  if (h.innerHTML !== html) { h.innerHTML = html; h.classList.toggle("mine", !!k); }
}
export function questionScreen(j) {
  const w = t();
  return `<section class="q">
    <h2>${w.asks}</h2>
    <blockquote>${esc(j.result || "").replace(/\n/g, "<br>")}</blockquote>
    <button class="btn primary" data-act="yes">${icon("check")}<span>${w.yes}</span></button>
    ${chipsHTML()}
  </section>`;
}

// clicks every model shares; a model handles its own data-act values first and returns true
export function wire(root, refresh, own = () => false) {
  root.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-act],[data-chip],[data-lang],[data-file],[data-style],[data-pick],[data-eg]");
    if (!b || (await own(b))) return;
    if (b.dataset.lang !== undefined) { setLang(lang === "th" ? "en" : "th"); return refresh(true); }
    if (b.dataset.pick) { await api.pick(b.dataset.pick); return refresh(true); }
    if (b.dataset.chip !== undefined) { b.disabled = true; await api.reply(CHIP_TH[+b.dataset.chip]); return refresh(true); }
    const a = b.dataset.act;
    if (a === "speak") return speak();
    if (a === "theme") { localStorage.theme = darkNow() ? "light" : "dark"; return applyTheme(); }
    if (a === "stop") await api.stop();
    if (a === "retry") await api.retry();
    if (a === "signin") await api.signin();
    if (a === "brand") await api.openBrand();
    if (a === "bk") bkOpen = !bkOpen;
    if (a === "bkuse") await api.brands("use", root.querySelector("#bklib").value);
    if (a === "bkstore") await api.brands("save", root.querySelector("#bkname").value);
    if (a === "fresh") await api.fresh();
    if (a === "ok") await api.reply("โอเค ทำไฟล์จริงเลย");
    if (a === "yes") await api.reply("ตกลง ทำต่อเลย ตัดสินใจเองได้");
    if (a === "show") await api.open("final");
    if (a === "folder") await api.open();
    if (a === "other") { const f = root.querySelector("form.other"); f.hidden = false; f.querySelector("input").focus(); return; }
    refresh(true);
  });
  root.addEventListener("change", async (e) => {   // a brand slot's file picker: the file goes to brand/ named by its role
    const r = e.target.dataset?.role; if (!r || !e.target.files?.length) return;
    await api.upload([...e.target.files], null, r); refresh(true);
  });
  root.addEventListener("submit", async (e) => {
    if (e.target.matches("form.bkform")) { e.preventDefault(); await api.brandTxt(Object.fromEntries(new FormData(e.target))); return refresh(true); }
    if (!e.target.matches("form.other")) return;
    e.preventDefault();
    const v = e.target.t.value.trim();
    if (v) { await api.reply(v); refresh(true); }
  });
}

// poll the server; re-render only when something the page shows has changed (so a playing video isn't reset)
export function poll(render) {
  let last = "", busy = false;
  const go = async (force) => {
    if (busy) return; busy = true;
    try {
      const s = await api.state();
      const key = JSON.stringify([lang, screen(s), s.job?.status, s.job?.step, s.job?.error, s.job?.slept, s.files.map((f) => f.name + f.size), s.net, s.brandId, s.signedIn, s.queue, s.waitUntil, (s.done || []).map((d) => d.id + d.status)]);
      if (force || key !== last) {
        const moved = last && JSON.parse(last)[1] !== screen(s);
        last = key;
        // a new screen slides in (View Transitions, native); a refresh of the same screen just updates in place
        if (moved && document.startViewTransition && !matchMedia("(prefers-reduced-motion: reduce)").matches) document.startViewTransition(() => render(s));
        else render(s);
      }
    } catch { render({ claude: true, net: false, files: [], job: { status: "error", error: "no_net", started: Date.now() }, offline: true }); }
    busy = false;
  };
  setLang(lang); go(true);
  setInterval(go, 2500);
  return go;
}

export function dropzone(target, onFiles) {   // the whole page accepts a dropped clip
  addEventListener("dragover", (e) => { e.preventDefault(); target.classList.add("over"); });
  addEventListener("dragleave", (e) => { if (!e.relatedTarget) target.classList.remove("over"); });
  addEventListener("drop", (e) => { e.preventDefault(); target.classList.remove("over"); if (e.dataTransfer.files.length) onFiles([...e.dataTransfer.files], e.target.closest?.("[data-role]")?.dataset.role); });   // on a brand slot: that role
}
export const fileInput = (id = "pick") => `<input type="file" id="${id}" accept="video/*,audio/*,.mov,.mp4,.m4a,.mp3,.wav" multiple hidden>`;

// read the screen aloud (Mac's own Thai voice "Kanya", offline): for people who'd rather listen than read
export function speak() {
  const sy = window.speechSynthesis; if (!sy) return;
  if (sy.speaking) return sy.cancel();
  const bot = [...document.querySelectorAll(".m:not(.me) .b")].at(-1);   // C: the newest thing TadClip said
  const parts = bot ? [bot] : [...document.querySelectorAll("main h1, main h2, #root h1, #root h2, .big, blockquote, .hint")];
  const text = parts.map((e) => e.innerText.trim()).filter(Boolean).join(" ... ");
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang === "th" ? "th-TH" : "en-US";
  u.voice = sy.getVoices().find((v) => v.lang.replace("_", "-").startsWith(u.lang)) || null;
  u.rate = 0.9; sy.speak(u);
}

applyTheme();   // last: it uses icon(), defined above
