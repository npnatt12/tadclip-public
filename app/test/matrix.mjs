// Every screen of one model in light/dark × Thai/English, with axe on each: node matrix.mjs [b] [--shots dir]
// Needs the replay test server (see check.mjs) and one finished replay run in its folder (check.mjs leaves one).
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const BASE = process.env.TADCLIP_URL || "http://127.0.0.1:4848";
const args = process.argv.slice(2), m = args.find((a) => /^[abc]$/.test(a)) || "b";
const si = args.indexOf("--shots"), SHOTS = si >= 0 ? args[si + 1] : "";
const AXE = fs.readFileSync(new URL("./node_modules/axe-core/axe.min.js", import.meta.url), "utf8");
const H = { "content-type": "application/json", origin: BASE };
const post = (p, b) => fetch(BASE + p, { method: "POST", headers: H, body: JSON.stringify(b || {}) });
const dir = (await (await fetch(BASE + "/api/state")).json()).folder;
const pv = path.join(dir, "IMG_2260", "finals", "TC01 - ClubGig (preview).mp4"), fin = path.join(dir, "IMG_2260", "finals", "TC01 - ClubGig.mp4");
const base = { id: "t", files: ["IMG_2260.MOV"], started: Date.now() - 9 * 60000, said: ["x"], session: "replay-0000" };
const summary = "ตัดคลิปตัวอย่างสไตล์ ClubGig เสร็จแล้ว ยาว 73 วินาที\nตัดช่วงขายคอร์สออกไปประมาณ 18 วินาที\nก่อนโพสต์ช่วยดูหน้าคนในภาพประกอบ 5 ช็อต";
const STATES = [
  ["home", null], ["styles", null],
  ["running", { ...base, status: "running", slept: Date.now() }],
  ["question", { ...base, status: "question", result: "ไม่พบโลโก้แบรนด์ ใช้โลโก้ Clubgig ได้ไหม\nถ้าไม่ตอบ จะใช้ Clubgig" }],
  ["preview", { ...base, status: "preview", preview: pv, result: summary }],
  ["final", { ...base, status: "final", preview: pv, final: fs.existsSync(fin) ? fin : pv, result: summary }],
  ...["no_claude", "signed_out", "no_net", "bad_file", "crashed", "stuck", "limit"].map((e) => [`err-${e}`, { ...base, status: "error", error: e, bad: e === "bad_file" ? "IMG_2260.MOV" : undefined }]),
  ["err-stopped", { ...base, status: "stopped" }],
].filter(([n]) => !(m === "a" && n === "styles"));   // A has no catalog: the folder always cuts ClubGig
const browser = await chromium.launch(), bad = [];
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
await post("/api/settings", { ui: m });
for (const theme of ["light", "dark"]) for (const lang of ["th", "en"]) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, colorScheme: theme });
  await page.addInitScript((l) => (localStorage.lang = l), lang);
  // the light/dark button: from the Mac's mode, one press must give the other mode for real (the page's background), and back
  await post("/api/test", { job: null });
  await page.goto(`${BASE}/${m}.html`); await page.waitForTimeout(1200);
  const bg = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  const light = (c) => +c.match(/\d+/)[0] > 128, start = light(await bg());
  if (start !== (theme === "light")) bad.push(`theme ${theme}/${lang}: page doesn't follow the Mac`);
  await page.click("[data-act=theme]"); await page.waitForTimeout(200);
  if (light(await bg()) === start) bad.push(`theme ${theme}/${lang}: the button didn't switch`);
  await page.reload(); await page.waitForTimeout(1200);
  if (light(await bg()) === start) bad.push(`theme ${theme}/${lang}: the choice wasn't kept after reload`);
  await page.click("[data-act=theme]"); await page.waitForTimeout(200);
  if (light(await bg()) !== start) bad.push(`theme ${theme}/${lang}: the button didn't switch back`);
  await page.evaluate(() => localStorage.removeItem("theme"));
  for (const [name, job] of STATES) {
    await post("/api/test", { job });
    await page.goto(`${BASE}/${m}.html`); await page.waitForTimeout(1500);
    if (name === "styles") { await page.locator(m === "c" ? "[data-file]:visible" : "[data-act=more]:visible").first().click(); await page.waitForTimeout(400);
      if (m === "c") { await page.locator("[data-act=pickstyle]").click(); } await page.waitForTimeout(1200); }
    await page.addScriptTag({ content: AXE });
    const v = await page.evaluate(() => axe.run(document, { resultTypes: ["violations"] }).then((r) => r.violations.filter((x) => ["serious", "critical"].includes(x.impact)).map((x) => `${x.id}(${x.nodes.length})`)));
    // the other language must not leak: no Thai on an English screen except the user's own words and the editor's summary
    const leak = lang === "en" ? await page.evaluate(() => [...document.querySelectorAll("h1,h2,button,.big,.muted,small,summary,label,li")]
      .filter((e) => !e.closest("details,blockquote,.said,[data-lang]") && /[฀-๿]/.test(e.innerText)).map((e) => e.innerText.trim().slice(0, 30)).slice(0, 3)) : [];
    if (v.length || leak.length) bad.push(`${name} ${theme}/${lang}: ${[...v, ...leak.map((x) => `thai-in-en:"${x}"`)].join(" ")}`);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${m}-${name}-${lang}-${theme}.png`) });
  }
  await page.close();
}
await post("/api/test", { job: null });
await browser.close();
console.log(`${m}: ${STATES.length} screens × 4 = ${STATES.length * 4} checked, ${bad.length} problems`);
for (const x of bad) console.log("  " + x);
