// The spotlight guide, step by step, in model B (~1 min). Starts its own server in replay/test mode on an empty folder.
//   node app/test/guide.mjs [shots dir]
// Each step: the right tip on the right screen; the tip never covers what it points at; what it points at still takes a
// click; axe has no violations; nothing runs off a 390 px screen at 125 % text; light and dark. Then: next walks the
// steps in order, skip stops them, "?" brings them back, a reload resumes after the last one done, and every step reaches
// the event log. Exit 1 on any failure.
import { chromium, webkit } from "playwright";   // TADCLIP_BROWSER=webkit: Safari's engine, as check.mjs
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const APP = path.join(path.dirname(fileURLToPath(import.meta.url)), ".."), SHOTS = process.argv[2] || "";
const AXE = fs.readFileSync(path.join(APP, "test/node_modules/axe-core/axe.min.js"), "utf8");
const PORT = 4877, BASE = `http://127.0.0.1:${PORT}`, DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tc-guide-"));
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
for (const n of ["a.mov", "b.mov"]) execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=360x640:d=4", "-pix_fmt", "yuv420p", path.join(DIR, n)]);
const prev = path.join(DIR, "a", "finals", "TC01 - ClubGig (preview).mp4"), fin = path.join(DIR, "a", "finals", "TC01 - ClubGig.mp4");
fs.mkdirSync(path.dirname(prev), { recursive: true }); fs.copyFileSync(path.join(DIR, "a.mov"), prev); fs.copyFileSync(path.join(DIR, "a.mov"), fin);
const srv = spawn(process.execPath, [path.join(APP, "server.mjs")], { env: { ...process.env, TADCLIP_PORT: String(PORT), TADCLIP_DIR: DIR, TADCLIP_TEST: "1", TADCLIP_REPLAY: path.join(APP, "test/fixture") }, stdio: "ignore" });
for (let i = 0; i < 50; i++) { try { await fetch(BASE + "/api/state"); break; } catch { await wait(200); } }
const H = { "content-type": "application/json", origin: BASE };
const setJob = (job) => fetch(BASE + "/api/test", { method: "POST", headers: H, body: JSON.stringify({ job }) });
const base = { id: "g", files: ["a.mov"], started: Date.now(), said: ["x"], session: "replay-0000" };
const JOBS = { running: { ...base, status: "running" }, preview: { ...base, status: "preview", preview: prev, result: "ได้คลิปตัวอย่างแล้ว" }, final: { ...base, status: "final", final: fin, result: "เสร็จแล้ว" } };

const bad = [];
const b = await (process.env.TADCLIP_BROWSER === "webkit" ? webkit : chromium).launch();
async function page(o = {}) {
  const ctx = await b.newContext({ viewport: { width: o.w || 900, height: 1000 }, colorScheme: o.dark ? "dark" : "light", reducedMotion: "reduce" });
  const p = await ctx.newPage(); await p.goto(BASE + "/b.html"); await p.waitForTimeout(2800); return p;
}
const tip = (p) => p.evaluate(() => { const b = document.querySelector(".gd-box"); return b && !b.hidden ? b.querySelector(".gd-t").textContent : null; });
// the tip's box vs the lit target: no overlap, the target still on screen and clickable at its centre
const geometry = (p) => p.evaluate(() => {
  const box = document.querySelector(".gd-box").getBoundingClientRect(), hole = document.querySelector(".gd-hole").getBoundingClientRect();
  const over = !(box.bottom <= hole.top + 6 || box.top >= hole.bottom - 6 || box.right <= hole.left + 6 || box.left >= hole.right - 6);
  const cx = hole.left + hole.width / 2, cy = hole.top + Math.min(hole.height / 2, 30), hit = document.elementFromPoint(cx, cy);
  return { over, onscreen: hole.bottom > 0 && hole.top < innerHeight, clickable: !!hit && !hit.closest(".gd-box,.gd-hole"),
    wide: document.documentElement.scrollWidth > innerWidth + 1, boxIn: box.left >= 0 && box.right <= innerWidth + 1 };
});
async function axe(p, name) {
  await p.addScriptTag({ content: AXE });
  const v = await p.evaluate(async () => (await axe.run({ runOnly: ["wcag2a", "wcag2aa"] })).violations.map((x) => `${x.id} ${x.nodes[0]?.target}`));
  if (v.length) bad.push(`${name}: axe ${v.join("; ")}`);
}
async function check(p, step, name) {
  const g = await geometry(p);
  if (g.over) bad.push(`${name}: the tip covers its target`);
  if (!g.onscreen) bad.push(`${name}: target off screen`);
  if (!g.clickable) bad.push(`${name}: target not clickable through the dim layer`);
  if (g.wide) bad.push(`${name}: page wider than the screen`);
  if (!g.boxIn) bad.push(`${name}: tip runs off the side`);
  await axe(p, name);
  if (SHOTS) await p.screenshot({ path: path.join(SHOTS, `guide-${name}.png`) });
}
const EXPECT = { home: ["clip", "style", "more", "wish", "brand", "batch", "start"], running: ["wait"], preview: ["change", "ok"], final: ["final"] };
const TEXT = { clip: "เลือกคลิป", style: "ClubGig", more: "แบบอื่น", wish: "ตัวอย่าง", brand: "โลโก้", batch: "หลายคลิป", start: "พร้อมแล้ว", signin: "เข้าสู่ระบบ", wait: "ปิดหน้านี้", change: "กดปุ่ม", ok: "ไฟล์จริง", final: "โฟลเดอร์" };

for (const o of [{ name: "light" }, { name: "dark", dark: true }, { name: "phone125", w: 390 }]) {
  await setJob(null);
  const p = await page(o);
  if (o.w) await p.evaluate(() => (document.documentElement.style.fontSize = "125%"));
  for (const n of ["a.mov", "b.mov"]) if ((await p.getAttribute(`[data-file="${n}"]`, "aria-pressed")) !== "true") await p.click(`[data-file="${n}"]`);   // two clips: the batch step too
  await p.waitForTimeout(600);
  for (const [scr, steps] of Object.entries(EXPECT)) {
    if (scr !== "home") { await setJob(JOBS[scr]); await p.waitForTimeout(3000); }
    for (const s of steps) {
      const t = await tip(p);
      if (!t || !t.includes(TEXT[s])) { bad.push(`${o.name}/${scr}: wanted "${s}", tip is ${JSON.stringify(t)}`); break; }
      const n = await p.evaluate(() => document.querySelector(".gd-box .gd-n")?.textContent || ""), want = steps.length > 1 ? `${steps.indexOf(s) + 1}/${steps.length}` : "";
      if (n !== want) bad.push(`${o.name}-${s}: counter "${n}", wanted "${want}"`);   // counted per screen, no number skipped
      await check(p, s, `${o.name}-${s}`);
      await p.click(".gd-box [data-gd=next]"); await p.waitForTimeout(300);
    }
    if (await tip(p)) bad.push(`${o.name}/${scr}: a tip still showing after the last step`);
  }
  await p.context().close();
}

// signed out: the sign-in tip on the sign-in button, and no start tip (there is no start button yet)
const signIn = (v) => fetch(BASE + "/api/test", { method: "POST", headers: H, body: JSON.stringify({ signedIn: v }) });
await setJob(null); await signIn(false);
{ const p = await page(), seen = [];
  for (let i = 0; i < 9 && (await tip(p)); i++) {
    const t = await tip(p); seen.push(t);
    if (t.includes(TEXT.signin)) await check(p, "signin", "light-signin");
    await p.click(".gd-box [data-gd=next]"); await p.waitForTimeout(300);
  }
  if (!seen.some((t) => t.includes(TEXT.signin))) bad.push(`signed out: no sign-in tip, saw ${JSON.stringify(seen)}`);
  if (seen.some((t) => t.includes(TEXT.start))) bad.push("signed out: the start tip showed with no start button");
  await p.context().close(); }
await signIn(true);
// keyboard and screen reader, skip, restart, resume, and the event log
{ const p = await page();
  const kb = await p.evaluate(() => ({ focus: document.activeElement?.dataset.gd, live: [...document.querySelectorAll(".sr[aria-live]")].pop()?.textContent }));
  if (kb.focus !== "next") bad.push(`keyboard: focus is not on ถัดไป (${kb.focus})`);
  if (!kb.live?.includes(TEXT.clip)) bad.push(`screen reader: the live region doesn't read the tip (${JSON.stringify(kb.live)})`);
  await p.keyboard.press("Enter"); await p.waitForTimeout(300);   // Enter on ถัดไป, no mouse
  await p.reload(); await p.waitForTimeout(2800);
  if (!(await tip(p))?.includes(TEXT.style)) bad.push(`resume: after a reload, wanted the step after "clip", got ${JSON.stringify(await tip(p))}`);
  await p.click(".gd-box [data-gd=skip]"); await p.waitForTimeout(300); await p.reload(); await p.waitForTimeout(2800);
  if (await tip(p)) bad.push("skip: tips came back after skipping");
  await p.click("[data-act=guidehelp]"); await p.waitForTimeout(800);
  if (!(await tip(p))?.includes(TEXT.clip)) bad.push(`restart: "?" should start again at the first step, got ${JSON.stringify(await tip(p))}`);
  await p.keyboard.press("Escape"); await p.waitForTimeout(300);
  if ((await tip(p))?.includes(TEXT.clip)) bad.push("Escape didn't move past the step");
  await p.context().close(); }
// the header is theirs once a brand is set: their name (and logo), TadClip small, no ClubGig wordmark
fs.writeFileSync(path.join(DIR, "brand", "brand.txt"), "ชื่อ: ร้านทดสอบ\nสีหลัก: #1F6FEB\n");
{ const p = await page();
  const h = await p.evaluate(() => { const b = document.querySelector(".top .brand"); return { text: b.textContent, clubgig: !!b.querySelector("img[src*=clubgig]"), mine: b.classList.contains("mine") }; });
  if (!h.text.includes("ร้านทดสอบ") || h.clubgig || !h.mine) bad.push(`brand header: ${JSON.stringify(h)}`);
  if (SHOTS) await p.screenshot({ path: path.join(SHOTS, "brand-header.png"), clip: { x: 0, y: 0, width: 900, height: 120 } });
  await p.context().close(); }
const ev = fs.readFileSync(path.join(DIR, ".tadclip", "events.log"), "utf8");
for (const s of [...Object.values(EXPECT).flat(), "signin"]) if (!ev.includes(`guide ${s} shown`)) bad.push(`event log: no "guide ${s} shown"`);
for (const a of ["guide clip next", "guide style skip", "guide all restart", "guide clip close"]) if (!ev.includes(a)) bad.push(`event log: no "${a}"`);

await b.close(); { const gone = new Promise((r) => srv.once("exit", r)); srv.kill(); await gone; }   // Windows: the folder is locked until it exits
fs.rmSync(DIR, { recursive: true, force: true, maxRetries: 20, retryDelay: 500 });
console.log(bad.length ? bad.map((x) => "FAIL " + x).join("\n") : `ok   guide: ${Object.values(EXPECT).flat().length} steps × light, dark, 390 px at 125 %, counter; sign-in step signed out; keyboard, live region, skip, restart, resume, Escape, event log, brand header`);
process.exit(bad.length ? 1 : 0);
