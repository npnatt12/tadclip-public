// Scores the three page models with checks instead of taste. Needs the app running in replay + test mode:
//   TADCLIP_PORT=4848 TADCLIP_TEST=1 TADCLIP_DIR=<empty dir> TADCLIP_REPLAY=app/test/fixture TADCLIP_REPLAY_SECONDS=8 node app/server.mjs
//   node app/test/check.mjs [a b c] [--shots <dir>]
// Per model: the task (clip in -> start -> progress -> preview -> one change -> OK -> final) counting clicks, screens and
// words read; axe-core (serious+critical) on every screen, light and dark; main button above the fold at 1280x720;
// no sideways overflow at 125 % text and at 390 px wide; every error screen reachable with one action.
import { chromium, webkit } from "playwright";   // TADCLIP_BROWSER=webkit: Safari's engine, the default browser on a fresh Mac
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const BASE = process.env.TADCLIP_URL || "http://127.0.0.1:4848";
const args = process.argv.slice(2), si = args.indexOf("--shots"), SHOTS = si >= 0 ? args[si + 1] : "";
const models = args.filter((a, i) => /^[abc]$/.test(a) && (si < 0 || i !== si + 1));
const AXE = fs.readFileSync(new URL("./node_modules/axe-core/axe.min.js", import.meta.url), "utf8");
const H = { "content-type": "application/json", origin: BASE };
const state = () => fetch(BASE + "/api/state").then((r) => r.json());
const post = (p, b) => fetch(BASE + p, { method: "POST", headers: H, body: JSON.stringify(b || {}) });
const ERRORS = ["no_claude", "signed_out", "no_net", "bad_file", "crashed", "stopped", "stuck", "limit"];

async function reset(m) {
  await post("/api/settings", { ui: m });   // else model A's folder watcher starts the clip under another model
  const s = await state();
  await post("/api/test", { job: null });
  for (const f of fs.readdirSync(s.folder)) if (!f.startsWith(".") && f !== "IMG_2260.MOV") fs.rmSync(path.join(s.folder, f), { recursive: true, force: true });
  if (!fs.existsSync(path.join(s.folder, "IMG_2260.MOV")))
    execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=720x1280:d=6", "-f", "lavfi", "-i", "sine=d=6", "-shortest", "-pix_fmt", "yuv420p", path.join(s.folder, "IMG_2260.MOV")]);
}
async function waitFor(pred, ms = 60000) {
  const t0 = Date.now();
  for (;;) { const s = await state(); if (pred(s)) return s; if (Date.now() - t0 > ms) throw new Error("timeout"); await new Promise((r) => setTimeout(r, 500)); }
}
async function words(page) {   // words a user has to read on screen now (Thai segmented by Intl.Segmenter)
  return page.evaluate(() => {
    const seg = new Intl.Segmenter("th", { granularity: "word" });
    let n = 0;
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) {
      const el = walk.currentNode.parentElement, r = el.getBoundingClientRect(), cs = getComputedStyle(el);
      if (!r.width || cs.visibility === "hidden" || el.closest("[hidden],script,style,.sr")) continue;
      for (const s of seg.segment(walk.currentNode.textContent)) if (s.isWordLike) n++;
    }
    return n;
  });
}
async function axe(page) {
  await page.addScriptTag({ content: AXE });
  const r = await page.evaluate(() => axe.run(document, { resultTypes: ["violations"] }));
  return r.violations.filter((v) => v.impact === "serious" || v.impact === "critical").map((v) => `${v.id}(${v.nodes.length})`);
}
async function settle(page) { await page.waitForTimeout(2900); }   // one poll + render

async function task(browser, m) {
  await reset(m);
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  let clicks = 0, wordsRead = 0, seen = new Set(), problems = [], perScreen = {};
  const click = async (sel) => { await page.locator(sel + ":visible").first().click(); clicks++; await settle(page); };
  const look = async (name) => {
    seen.add(name); const n = await words(page); wordsRead += n; perScreen[name] = n;
    const said = await page.evaluate(() => { window.__said = ""; speechSynthesis.speak = (u) => (window.__said = u.text); document.querySelector("[data-act=speak]")?.click(); return new Promise((r) => setTimeout(() => r(window.__said), 300)); });
    if (!/[\u0E00-\u0E7F]/.test(said)) problems.push(`${name}: ฟัง read nothing in Thai`);
    if (["preview", "final"].includes(name)) {   // the main button must be on screen without scrolling here too
      const bx = await page.locator(".btn.primary:visible").first().boundingBox().catch(() => null);
      if (!bx || bx.y + bx.height > 720) problems.push(`${name}: main button below the fold`);
    }
    const v = await axe(page); if (v.length) problems.push(`${name}: ${v.join(" ")}`);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${m}-${name}-th-light.png`) });
  };
  const clip = path.join((await state()).folder, "IMG_2260.MOV"), aside = clip + ".aside";
  if (m === "a") fs.renameSync(clip, aside);   // model A: the folder starts empty; the clip "arrives" after the page opens
  await page.goto(`${BASE}/${m}.html`); await settle(page);
  await look("home");
  if (m === "a") fs.renameSync(aside, clip);   // = the user dropping it into ~/TadClip in Finder
  let tabs = 0;   // keyboard: Tab presses from the top of the page to the main button
  for (; tabs < 20; ) { await page.keyboard.press("Tab"); tabs++; if (await page.evaluate(() => document.activeElement?.matches(".btn.primary"))) break; }
  const primary = page.locator(".btn.primary").first();
  const box = await primary.boundingBox().catch(() => null);
  const fold = !!box && box.y + box.height <= 720;
  if (m === "b") { await click("[data-act=more]"); await look("styles"); await click("[data-style=route]"); await click("[data-act=go]"); }
  if (m === "c") { await click("[data-file]"); await look("confirm"); await click("[data-act=pickstyle]"); await look("styles"); await click("[data-style=route]"); await click("[data-act=go]"); }
  // a: nothing to press, the folder watcher starts the clip that is already in the folder
  const t0 = Date.now();
  await waitFor((s) => ["running", "preview"].includes(s.job?.status), 30000); await settle(page);
  const toStart = Math.round((Date.now() - t0) / 100) / 10;
  const asked = (await state()).job?.said?.[0] || "";
  if (m !== "a" && !asked.includes("Route maps")) problems.push("the chosen effect did not reach the message");
  await look("running");
  await waitFor((s) => s.job?.status === "preview"); await settle(page);
  await look("preview");
  await click("[data-chip='0']");   // "สว่างขึ้น", then Stop halfway: they must land back on the preview they had
  await waitFor((s) => s.job?.status === "running");
  await click("[data-act=stop]");
  const back = await waitFor((s) => s.job?.status !== "running", 10000);
  if (back.job?.status !== "preview") problems.push(`stop during a change lost the preview (${back.job?.status})`);
  await click("[data-chip='0']");
  await waitFor((s) => s.job?.status === "preview" && s.job.said.length === 3); await settle(page);
  await click("[data-act=ok]");
  await waitFor((s) => s.job?.status === "final"); await settle(page);
  await look("final");
  await page.close();
  return { clicks, screens: seen.size, wordsRead, fold, problems, toStart, tabs, perScreen };
}

async function layout(browser, m) {   // 125 % text and a narrow window: nothing may run off the side
  const out = [];
  await reset(m);
  for (const [w, h, fs125] of [[1280, 720, true], [390, 844, false], [390, 844, true]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto(`${BASE}/${m}.html`); await settle(page);
    if (fs125) await page.addStyleTag({ content: "html{font-size:25px!important}" });
    await page.waitForTimeout(300);
    const over = await page.evaluate(() => {
      const bad = [];
      if (document.documentElement.scrollWidth > innerWidth + 1) bad.push(`page ${document.documentElement.scrollWidth}>${innerWidth}`);
      for (const el of document.querySelectorAll("button,a,h1,h2,p,span,b,small")) {
        const r = el.getBoundingClientRect();
        if (r.width && (r.right > innerWidth + 1 || el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === "hidden")) bad.push(el.textContent.trim().slice(0, 24));
      }
      return bad.slice(0, 4);
    });
    if (over.length) out.push(`${w}px${fs125 ? "@125%" : ""}: ${over.join(" | ")}`);
    await page.close();
  }
  return out;
}

async function errors(browser, m) {   // every error screen: reachable, says what happened, one action, passes axe
  const out = [];
  for (const theme of ["light", "dark"]) for (const code of ERRORS) {
    await post("/api/test", { job: { id: "t", files: ["IMG_2260.MOV"], status: code === "stopped" ? "stopped" : "error", error: code === "stopped" ? null : code, started: Date.now(), session: "replay-0000", bad: code === "bad_file" ? "IMG_2260.MOV" : undefined } });
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, colorScheme: theme });
    await page.goto(`${BASE}/${m}.html`); await settle(page);
    const text = await page.locator("body").innerText();
    const actions = await page.locator(".btn.primary:visible").count();
    const v = await axe(page);
    if (!/[฀-๿]/.test(text)) out.push(`${code}: no Thai text`);
    if (actions < 1) out.push(`${code}/${theme}: no main action`);
    if (v.length) out.push(`${code}/${theme}: ${v.join(" ")}`);
    if (SHOTS && theme === "light") await page.screenshot({ path: path.join(SHOTS, `${m}-err-${code}-th-light.png`) });
    await page.close();
  }
  await post("/api/test", { job: null });
  return out;
}

async function dark(browser, m) {   // home + preview in dark, English too
  const out = [];
  for (const [theme, lang] of [["light", "th"], ["dark", "th"], ["light", "en"], ["dark", "en"]]) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, colorScheme: theme });
    await page.addInitScript((l) => (localStorage.lang = l), lang);
    for (const [name, job] of [["home", null], ["running", { id: "t", files: ["IMG_2260.MOV"], status: "running", started: Date.now() - 600000, said: ["x"], slept: Date.now() }],
      ["preview", { id: "t", files: ["IMG_2260.MOV"], status: "preview", started: Date.now(), said: ["x"], session: "replay-0000", preview: "PREVIEW", result: "ตัดคลิปตัวอย่างสไตล์ ClubGig เสร็จแล้ว ยาว 73 วินาที" }],
      ["question", { id: "t", files: ["IMG_2260.MOV"], status: "question", started: Date.now(), said: ["x"], session: "replay-0000", result: "ไม่พบโลโก้แบรนด์ ใช้โลโก้ Clubgig ได้ไหม\nถ้าไม่ตอบ จะใช้ Clubgig" }]]) {
      if (job?.preview === "PREVIEW") { const d = (await state()).folder; job.preview = path.join(d, "IMG_2260", "finals", "TC01 - ClubGig (preview).mp4"); if (!fs.existsSync(job.preview)) continue; }
      await post("/api/test", { job });
      await page.goto(`${BASE}/${m}.html`); await settle(page);
      const v = await axe(page); if (v.length) out.push(`${name}/${theme}/${lang}: ${v.join(" ")}`);
      if (SHOTS && !(theme === "light" && lang === "th" && ["home", "running", "preview"].includes(name))) await page.screenshot({ path: path.join(SHOTS, `${m}-${name}-${lang}-${theme}.png`) });
    }
    await page.close();
  }
  await post("/api/test", { job: null });
  return out;
}

// 11-09: a picture dropped on the page must go to brand/ and show up as their logo, not join the clips
async function intake() {
  const s0 = await state(), png = fs.readFileSync(new URL("./fixture/logo.png", import.meta.url));
  const r = await (await fetch(`${BASE}/api/upload?name=my-logo.png`, { method: "POST", headers: { origin: BASE }, body: png })).json();
  let s = s0; for (let i = 0; i < 20 && !s.brand?.have?.logo; i++) { await new Promise((ok) => setTimeout(ok, 500)); s = await state(); }
  const bad = [];
  if (r.to !== "brand" || !fs.existsSync(path.join(s.folder, "brand", "my-logo.png"))) bad.push("a dropped picture did not go to brand/");
  if (s.files.some((f) => f.name === "my-logo.png")) bad.push("a dropped picture joined the clips");
  if (s.brand?.have?.logo !== "file") bad.push("the page doesn't show the dropped logo as taken in");
  fs.rmSync(path.join(s.folder, "brand", "my-logo.png"), { force: true });
  return bad;
}
// 11-10: the brand panel. A slot per asset (named by role, the last one replaced), every colour of a sheet with the brand's
// own text colour on its plate, the typed fields -> brand.txt, the library, a loader crash shown on the page
async function brandPanel(browser) {
  const bad = [], s0 = await state(), B = path.join(s0.folder, "brand"), up = (name, role, body) => fetch(`${BASE}/api/upload?name=${encodeURIComponent(name)}&role=${role}`, { method: "POST", headers: { origin: BASE }, body });
  const until = async (pred) => { let s; for (let i = 0; i < 40; i++) { s = await state(); if (pred(s)) return s; await new Promise((ok) => setTimeout(ok, 500)); } return s; };
  const fx = (f) => fs.readFileSync(new URL(`./fixture/${f}`, import.meta.url));
  for (const f of fs.readdirSync(B)) fs.rmSync(path.join(B, f), { recursive: true, force: true });
  await up("first.png", "logo", fx("logo.png")); await up("my logo v2.png", "logo", fx("logo.png")); await up("colours.png", "sheet", fx("brand-sheet.png"));
  const logos = fs.readdirSync(B).filter((f) => /logo/i.test(f));
  if (logos.join() !== "logo.png") bad.push(`a second logo didn't replace the first: ${logos}`);
  let s = await until((x) => x.brand?.colors?.list?.length === 3);
  if ((s.brand?.colors?.list || []).map((c) => c.hex).join(" ") !== "#00CCFF #A0ECFF #344054") bad.push(`the sheet's colours: ${JSON.stringify(s.brand?.colors?.list)}`);
  if (s.brand?.impact?.plate !== "#00CCFF" || s.brand?.impact?.ink !== "#344054") bad.push(`the cyan plate with Oxford Blue text: ${JSON.stringify(s.brand?.impact)}`);
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto(BASE + "/"); await page.waitForSelector("[data-act=bk]"); await page.click("[data-act=bk]"); await page.waitForSelector(".bkpanel");
  if (await page.locator(".slot").count() !== 5) bad.push("the panel doesn't show 5 slots");
  const pl = await page.locator(".proof .pl").first().evaluate((e) => [getComputedStyle(e).backgroundColor, getComputedStyle(e).color]);
  if (pl.join() !== "rgb(0, 204, 255),rgb(52, 64, 84)") bad.push(`the proof's plate: ${pl}`);
  const v = await axe(page); if (v.length) bad.push(`brand panel axe: ${v.join(" ")}`);
  await page.fill("#f-name", "Test Clinic"); await page.fill("#f-line", "@testclinic"); await page.click(".bkform [type=submit]");
  s = await until((x) => x.brand?.typed?.line === "@testclinic");
  const txt = fs.existsSync(path.join(B, "brand.txt")) ? fs.readFileSync(path.join(B, "brand.txt"), "utf8") : "";
  if (!/ชื่อ: Test Clinic/.test(txt) || !/LINE: @testclinic/.test(txt) || /สีหลัก/.test(txt)) bad.push(`brand.txt from the fields: ${JSON.stringify(txt)}`);
  if (s.brand?.colors?.list?.length !== 3) bad.push("typing a name and LINE dropped the sheet's colours");
  await post("/api/brands", { act: "save", name: "Test Clinic" }); await post("/api/brands", { act: "use", name: "" });
  s = await until((x) => !x.brand);
  if (!s.brands?.includes("Test Clinic") || s.brand) bad.push(`library: saved ${JSON.stringify(s.brands)}, ClubGig after "no brand": ${!s.brand}`);
  await post("/api/brands", { act: "use", name: "Test Clinic" }); s = await until((x) => x.brand?.name === "Test Clinic");
  if (s.brand?.name !== "Test Clinic") bad.push("using a saved brand didn't bring it back");
  fs.rmSync(path.join(B, "brand.txt"), { force: true }); fs.mkdirSync(path.join(B, "brand.txt"));   // a brand.txt the loader can't read at all: said on the page, not a silent ClubGig
  s = await until((x) => x.brand?.error); await page.reload(); await page.waitForSelector("[data-act=bk]");
  if (!s.brand?.error || !(await page.locator(".bkerr").count())) bad.push("a loader crash isn't shown on the page");
  fs.rmSync(path.join(B, "brand.txt"), { recursive: true }); await page.close();
  for (const f of fs.readdirSync(B)) fs.rmSync(path.join(B, f), { recursive: true, force: true });
  fs.rmSync(path.join(s0.folder, "brands"), { recursive: true, force: true });
  return bad;
}
const browser = await (process.env.TADCLIP_BROWSER === "webkit" ? webkit : chromium).launch();
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
const report = {};
for (const m of models.length ? models : ["a", "b", "c"]) {
  const r = await task(browser, m);
  r.themes = await dark(browser, m);   // first: it shows the preview the task just made; layout() clears the folder
  r.layout = await layout(browser, m);
  r.errors = await errors(browser, m);
  if (m === "b") r.errors.push(...await intake(), ...await brandPanel(browser));
  r.fails = r.problems.length + r.layout.length + r.errors.length + r.themes.length + (r.fold ? 0 : 1);
  report[m] = r;
  console.log(`${m}: clicks ${r.clicks}, screens ${r.screens}, words ${r.wordsRead} ${JSON.stringify(r.perScreen)}, tabs ${r.tabs}, start ${r.toStart}s, fold ${r.fold ? "ok" : "BELOW"}, fails ${r.fails}`);
  for (const k of ["problems", "layout", "errors", "themes"]) for (const x of r[k]) console.log(`   ${k}: ${x}`);
}
await browser.close();
fs.writeFileSync(new URL("./last-report.json", import.meta.url), JSON.stringify(report, null, 1));
