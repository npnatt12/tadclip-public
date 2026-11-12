// Real screenshots of the TadClip page for the user manual, every step a buyer sees, from the replay test server (no one's
// footage, no network): node manual-shots.mjs <out dir> [brand dir ...]
// Start the server first, as check.mjs does: TADCLIP_PORT=4848 TADCLIP_TEST=1 TADCLIP_DIR=<tmp> TADCLIP_REPLAY=app/test/fixture
// node app/server.mjs, and run check.mjs b once so a finished replay run exists. Each brand dir (logo + brand.txt) is copied
// into the TadClip folder's brand/ for its own brand-panel shots (example brands; never a real shop's files).
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const BASE = process.env.TADCLIP_URL || "http://127.0.0.1:4848";
const [OUT, ...BRANDS] = process.argv.slice(2);
if (!OUT) { console.log("node manual-shots.mjs <out dir> [brand dir ...]"); process.exit(2); }
fs.mkdirSync(OUT, { recursive: true });
const H = { "content-type": "application/json", origin: BASE };
const post = (p, b) => fetch(BASE + p, { method: "POST", headers: H, body: JSON.stringify(b || {}) });
const st = await (await fetch(BASE + "/api/state")).json(), dir = st.folder;
const pv = path.join(dir, "IMG_2260", "finals", "TC01 - ClubGig (preview).mp4"), fin = path.join(dir, "IMG_2260", "finals", "TC01 - ClubGig.mp4");
const base = { id: "t", files: ["IMG_2260.MOV"], started: Date.now() - 9 * 60000, said: ["ขอ hook แรงๆ ตัวหนังสือกลางอก"], session: "replay-0000" };
const summary = "ตัดคลิปตัวอย่างสไตล์ ClubGig เสร็จแล้ว ยาว 73 วินาที\nตัดช่วงพูดซ้ำออกไปประมาณ 18 วินาที\nก่อนโพสต์ช่วยดูหน้าคนในภาพประกอบ 5 ช็อต";
const brandDir = path.join(dir, "brand");

await post("/api/settings", { ui: "b" });
const browser = await chromium.launch();
const shots = [];
async function shot(name, { job = null, signedIn = true, act, brand, width = 1280, height = 820, full = false, lang = "th", tips = false, el } = {}) {
  await post("/api/test", { job, signedIn });
  const page = await browser.newPage({ viewport: { width, height }, colorScheme: "light", deviceScaleFactor: 2 });
  await page.addInitScript((l) => { localStorage.lang = l; localStorage.removeItem("tcGuide"); }, lang);
  await page.goto(`${BASE}/b.html`); await page.waitForTimeout(1500);
  if (!tips) { const skip = page.locator(".gd-box button", { hasText: /ข้ามคำแนะนำ|Skip tips/ }); if (await skip.count()) { await skip.first().click(); await page.waitForTimeout(300); } }
  if (act) { await act(page); await page.waitForTimeout(900); }
  // style tiles and the preview player: wait for real frames, not empty boxes
  await page.evaluate(async () => { for (const v of document.querySelectorAll("video")) { v.muted = true; v.preload = "auto";
    await new Promise((r) => { if (v.readyState >= 2) return r(); v.addEventListener("loadeddata", r, { once: true }); v.load(); setTimeout(r, 4000); });
    try { v.currentTime = Math.min(2.5, (v.duration || 3) / 2); } catch {} } });
  await page.waitForTimeout(1200);
  const f = path.join(OUT, `${name}.png`);
  if (el) {   // one panel, without the floating "ตัดต่อให้หน่อย" bar over it
    await page.addStyleTag({ content: "section.go{visibility:hidden!important}" });
    await page.locator(el).first().screenshot({ path: f });
  } else await page.screenshot({ path: f, fullPage: full });
  shots.push(name);
  await page.close();
}
const setBrand = (src) => {   // the TadClip folder's brand/ = this example brand's files only
  fs.rmSync(brandDir, { recursive: true, force: true }); fs.mkdirSync(brandDir, { recursive: true });
  if (src) for (const f of fs.readdirSync(src)) fs.copyFileSync(path.join(src, f), path.join(brandDir, f));
};
const openBrand = async (p) => { const b = p.locator("[data-act=bk]").first(); await b.scrollIntoViewIfNeeded(); await b.click(); };
const openStyles = async (p) => { await p.locator("[data-act=more]:visible").first().click().catch(() => {}); };

setBrand(null);
await shot("01-home-signed-out", { signedIn: false, tips: true });
await shot("02-home");
await shot("03-brand-empty", { act: openBrand, el: "section.step >> nth=1" });
for (const [i, b] of BRANDS.entries()) {
  setBrand(b);
  await shot(`04-brand-${path.basename(b)}`, { act: openBrand, el: "section.step >> nth=1" });
  await shot(`05-home-${path.basename(b)}`);
}
setBrand(BRANDS[0] || null);
await shot("06-styles", { act: openStyles, el: "section.step >> nth=1" });
await shot("07-running", { job: { ...base, status: "running", slept: Date.now() } });
await shot("08-preview", { job: { ...base, status: "preview", preview: pv, result: summary }, full: true });
await shot("09-final", { job: { ...base, status: "final", preview: pv, final: fs.existsSync(fin) ? fin : pv, result: summary }, full: true });
await shot("10-error-signed-out", { job: { ...base, status: "error", error: "signed_out" } });
await shot("11-phone-home", { width: 390, height: 844 });
await post("/api/test", { job: null, signedIn: true });
setBrand(null);
await browser.close();
console.log(`${shots.length} shots in ${OUT}: ${shots.join(", ")}`);
