#!/usr/bin/env node
// TadClip app: one local page that starts a TadClip run through headless Claude Code, so a first-time user never types.
// Node 22, stdlib only. Listens on 127.0.0.1 only; POSTs must come from this page (Origin + Host checked).
//   node app/server.mjs [--open]            TADCLIP_DIR (default ~/TadClip) is the folder the user puts clips in
//   TADCLIP_REPLAY=<dir> node app/server.mjs  replays a recorded run (stream.jsonl, progress.log, preview.mp4) in ~20 s
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn, execFile } from "node:child_process";
import { fileURLToPath } from "node:url";

const HOME = os.homedir();
const APP = path.dirname(fileURLToPath(import.meta.url));
const PORT = +(process.env.TADCLIP_PORT || 4747);
const DIR = process.env.TADCLIP_DIR || path.join(HOME, "TadClip");
const STATE = path.join(DIR, ".tadclip");
const REPLAY = process.env.TADCLIP_REPLAY ? path.resolve(process.env.TADCLIP_REPLAY) : "";   // resolved: the replay runs with cwd = the clip folder
let testSignedIn = true;   // test mode only: replay is always signed in, so /api/test can sign it out to check the sign-in step
const TEST = process.env.TADCLIP_TEST === "1";   // lets the checks force any error screen
const PATHX = [`${HOME}/.local/bin`, "/opt/homebrew/opt/node@22/bin", "/opt/homebrew/bin", "/usr/local/bin", process.env.PATH].join(":");
const VIDEO = /\.(mov|mp4|m4v|avi|mkv|mts|3gp|hevc|webm)$/i, AUDIO = /\.(mp3|m4a|wav|aac|aif|aiff|flac|ogg)$/i;
const TOOLS = "Bash,Read,Write,Edit,Glob,Grep,Agent,Skill,TodoWrite";
fs.mkdirSync(STATE, { recursive: true });
// their own brand: whatever they put in ~/TadClip/brand/ (scripts/own_brand.py, docs/BRAND-KIT.md). The page shows what
// was picked up; the summary is re-read only when the folder changes.
const BRAND = path.join(DIR, "brand");
fs.mkdirSync(BRAND, { recursive: true });
if (!fs.readdirSync(BRAND).length) fs.writeFileSync(path.join(BRAND, "วางโลโก้ที่นี่.txt"),
  "วางไฟล์ของแบรนด์ไว้ในโฟลเดอร์นี้ คลิปต่อไปจะใช้แบรนด์ของคุณ (ไม่ใส่อะไรเลย = ใช้แบรนด์ ClubGig)\n\n" +
  "ง่ายที่สุด: เปิดหน้า TadClip กด \"แก้แบรนด์\" แล้ววางไฟล์ในช่องของมัน\n\n" +
  "- โลโก้: ภาพไหนก็ได้ (PNG JPG HEIC SVG PDF) รูปโปรไฟล์ LINE หรือ Facebook ก็ใช้ได้\n- ชีตสีแบรนด์ / คู่มือแบรนด์ (ภาพหรือ PDF ที่มีรหัสสี #) TadClip อ่านทุกสี\n- หรือภาพหน้าจอเพจของคุณ 1 ภาพ (TadClip หาสีแบรนด์จากภาพนี้)\n" +
  "- ไม่ใส่ก็ได้: ไฟล์ชื่อ brand.txt เขียนแบบนี้\n    ชื่อ: ร้านของฉัน\n    สีหลัก: #1F6FEB\n    สีรอง: #F5B700\n    ฟอนต์: Prompt\n" +
  "    สโลแกน: อร่อย / ทุกวัน\n    LINE: @myshop\n    ปุ่ม LINE: สั่งเลย / สอบถาม\n    ห้ามใช้: ภาพเด็ก\n- ฟอนต์ของแบรนด์: วางไฟล์ .ttf หรือ .otf ที่มีภาษาไทย\n\n" +
  "Put your brand here: a logo (a LINE or Facebook profile picture works), or one screenshot of your page, and if you like a brand.txt\n" +
  "and a .ttf font. The next clip uses it.\n");
let brandCache = { key: null, kit: null };
async function brand() {
  fs.mkdirSync(BRAND, { recursive: true });   // they may have deleted it
  let key = ""; try { key = fs.readdirSync(BRAND).filter((f) => !f.startsWith(".")).map((f) => f + fs.statSync(path.join(BRAND, f)).mtimeMs).join("|"); } catch {}
  if (key === brandCache.key) return brandCache;
  const r = await run("python3", [path.join(APP, "..", "scripts", "own_brand.py"), "--show", "--from", BRAND], 90000);   // OCR + conversions: a few s
  let kit = null; try { kit = JSON.parse(r.out); } catch {}
  // never silent (11-10 test: a font file crashed the loader and the page quietly showed ClubGig): the reason, on the page and in the log
  if (r.code || (!kit && key && r.out.trim() !== "null")) kit = { error: (r.err.trim().split("\n").pop() || `exit ${r.code}`).slice(0, 200) };
  brandCache = { key, kit, id: String(key.length) + key.slice(-24) + (kit?.error ? "e" : "") };
  log("brand", kit?.error ? `error ${JSON.stringify(kit.error)}` : kit ? `${(kit.colors?.list || []).map((c) => c.hex).join(" ") || "-"} font=${kit.font_name || "-"} files=${JSON.stringify(kit.files)} ${JSON.stringify(kit.notes)}` : "none (ClubGig)");
  return brandCache;
}
// the brand library: ~/TadClip/brands/<name>/, each a copy of a brand folder (a team shares one by copying its folder)
const BRANDS = path.join(DIR, "brands");
const brandNames = () => { try { return fs.readdirSync(BRANDS).filter((f) => !f.startsWith(".") && fs.statSync(path.join(BRANDS, f)).isDirectory()).sort(); } catch { return []; } };
const safeName = (n) => String(n || "").replace(/[\/:\\]/g, " ").replace(/^\.+/, "").trim().slice(0, 60);
const own = (d) => fs.existsSync(d) ? fs.readdirSync(d).filter((f) => !f.startsWith(".") && !/^วางโลโก้ที่นี่\.txt$/.test(f)) : [];
function saveBrand(name) {   // brand/ -> brands/<name>/ (replaced)
  const to = path.join(BRANDS, safeName(name)); if (!safeName(name) || !own(BRAND).length) return false;
  fs.rmSync(to, { recursive: true, force: true }); fs.mkdirSync(to, { recursive: true });
  for (const f of own(BRAND)) fs.copyFileSync(path.join(BRAND, f), path.join(to, f));
  return true;
}
// brand.txt from the page's fields (11-10 tester: "typing the brand needs a hand-written brand.txt in Finder")
const TXT = [["name", "ชื่อ"], ["primary", "สีหลัก"], ["secondary", "สีรอง"], ["light", "สีอ่อน"], ["dark", "สีเข้ม"], ["font", "ฟอนต์"],
  ["tagline", "สโลแกน"], ["line", "LINE"], ["linebutton", "ปุ่ม LINE"], ["avoid", "ห้ามใช้"]];
// one timestamped line per event, for test runs and bug reports (scripts/logs.sh collects it)
const EV = path.join(STATE, "events.log");
// never throws: a full disk made appendFileSync throw inside a request handler, which ends the whole server (Node 22)
const log = (...a) => { try { fs.appendFileSync(EV, `${new Date().toISOString()} ${a.join(" ")}\n`); } catch {} };

const run = (cmd, args, ms = 15000) => new Promise((ok) =>
  execFile(cmd, args, { timeout: ms, env: { ...process.env, PATH: PATHX } }, (e, out, err) => ok({ code: e ? (e.code ?? 1) : 0, out: String(out), err: String(err) })));

// the claude binary: the CLI if installed, else the one the Claude desktop app keeps for its Code tab
function claudeBin() {
  const c = [process.env.TADCLIP_CLAUDE, `${HOME}/.local/bin/claude`, "/opt/homebrew/bin/claude", "/usr/local/bin/claude"];
  const app = path.join(HOME, "Library/Application Support/Claude/claude-code");
  try {
    for (const v of fs.readdirSync(app).sort().reverse())
      for (const h of fs.readdirSync(path.join(app, v))) c.push(path.join(app, v, h, "claude.app/Contents/MacOS/claude"));
  } catch {}
  return c.find((p) => p && fs.existsSync(p)) || "";
}

// ---- checks before a run: each failure is one error screen with one thing to do ----
let netCache = { t: 0, ok: true };
async function online() {
  if (Date.now() - netCache.t < 20000) return netCache.ok;
  let ok = false;
  try { await fetch("https://api.anthropic.com", { method: "HEAD", signal: AbortSignal.timeout(5000) }); ok = true; } catch {}
  return (netCache = { t: Date.now(), ok }).ok;
}
// sign-in: checked before the start button too (11-09 evening: the start failed first, then sign-in). Each change is
// logged with its method and expiry (never the e-mail): that account lost a sign-in made the same morning, cause unknown.
let auth = { t: 0, ok: null, key: "" };
async function signedIn(bin, fresh = true) {
  if (!fresh && Date.now() - auth.t < 60000) return auth.ok;
  const r = await run(bin, ["auth", "status"]); let ok, j = {};
  try { j = JSON.parse(r.out); ok = j.loggedIn === true; } catch { ok = r.code === 0; }
  const key = `${ok} ${j.authMethod || "-"} expires=${j.loginExpiresAt || "-"}`;
  if (key !== auth.key) log("auth", key);
  auth = { t: Date.now(), ok, key };
  return ok;
}
async function probe(file) {   // a video the editor can read: has a picture and is longer than 3 s
  const r = await run("ffprobe", ["-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", file]);
  try {
    const j = JSON.parse(r.out);
    return j.streams.some((s) => s.codec_type === "video") && +j.format.duration > 3;
  } catch { return false; }
}

// ---- the job: one at a time, saved so a restart (or a reboot) still knows where it was ----
const JOB = path.join(STATE, "job.json");
let job = fs.existsSync(JOB) ? JSON.parse(fs.readFileSync(JOB, "utf8")) : null;
let child = null;
// every job is also kept in jobs/<id>.json: a batch makes several, and any finished one can be opened again for changes
const JOBS = path.join(STATE, "jobs");
fs.mkdirSync(JOBS, { recursive: true });
const save = () => { fs.writeFileSync(JOB, JSON.stringify(job, null, 1)); if (job?.id) fs.writeFileSync(path.join(JOBS, `${job.id}.json`), JSON.stringify(job)); };
const history = () => fs.readdirSync(JOBS).filter((f) => f.endsWith(".json")).sort().reverse().slice(0, 12).map((f) => {
  try { const j = JSON.parse(fs.readFileSync(path.join(JOBS, f), "utf8")); return { id: j.id, name: (j.files || []).find((x) => VIDEO.test(x)) || "", status: j.status, error: j.error || null, batch: !!j.batch }; } catch { return null; }
}).filter(Boolean);

// Claude's 5-hour usage window, read off the run's own stream (rate_limit_event). Measured 11-09/10: one reel used 14-46 %
// of it on Pro, so a queue starts the next clip only under HEADROOM and otherwise waits for the reset; a run that hits
// the limit carries on by itself after the reset (it used to stop on an error screen: "wait until Claude says, press Carry on")
const USAGE = path.join(STATE, "usage.json"), HEADROOM = +(process.env.TADCLIP_HEADROOM || 0.55), PAD = +(process.env.TADCLIP_RESUME_PAD_MS ?? 60000);   // a minute past the reset
let usage = (() => { try { return JSON.parse(fs.readFileSync(USAGE, "utf8")); } catch { return null; } })();
const QUEUE = path.join(STATE, "queue.json");
let queue = (() => { try { return JSON.parse(fs.readFileSync(QUEUE, "utf8")); } catch { return []; } })();
const saveQ = () => fs.writeFileSync(QUEUE, JSON.stringify(queue));
const paceUntil = () => usage && usage.five >= HEADROOM && usage.resetsAt + PAD > Date.now() ? usage.resetsAt + PAD : 0;
if (job?.status === "running") { job.status = "error"; job.error = "crashed"; save(); }   // the app stopped mid-run

function newest(glob) {   // glob: [subdir pattern] -> newest file under DIR/*/<sub> matching re, after t
  const [sub, re, after] = glob; let best = null;
  for (const d of fs.readdirSync(DIR, { withFileTypes: true })) {
    if (!d.isDirectory() || d.name.startsWith(".")) continue;
    const p = path.join(DIR, d.name, sub);
    let names = []; try { names = fs.readdirSync(p); } catch { continue; }
    for (const n of names) if (re.test(n)) {
      const f = path.join(p, n), m = fs.statSync(f).mtimeMs;
      if (m >= after && (!best || m > best.m)) best = { f, m };
    }
  }
  return best?.f || "";
}

let lastLine = "";
function progress() {
  const t0 = (job?.turnStarted || job?.started || 0) - 5000;   // this turn's lines only: an OK must not show the build's "9/9"
  const plog = job && newest(["build", /^progress\.log$/, t0]);
  if (!plog) return { lines: [] };
  // ponytail: lines carry HH:MM only; across midnight the filter is off (the old lines may show until the first new one)
  const hm = (d) => `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`, since = hm(new Date(t0));
  const lines = fs.readFileSync(plog, "utf8").trim().split("\n").filter((l) => l && (since > hm(new Date()) || l.slice(0, 5) >= since || !/^\d\d:\d\d/.test(l))).slice(-40);
  if (lines.length && lines.at(-1) !== lastLine) { lastLine = lines.at(-1); log("step", `job=${job.id}`, JSON.stringify(lastLine)); }
  const m = lines.at(-1)?.match(/\[(\d+)\/(\d+)\]\s*(.*)/);
  const [th, en] = (m?.[3] || "").split(" | ");
  return { lines, step: m ? { n: +m[1], of: +m[2], th: th?.trim(), en: (en || th)?.trim() } : null };
}

function message(files, style, wish, batch) {
  const vids = files.filter((f) => VIDEO.test(f)).map((f) => path.join(DIR, f));
  const auds = files.filter((f) => AUDIO.test(f)).map((f) => path.join(DIR, f));
  let m = `ตัดต่อคลิปนี้ ${vids.join(" ")}`;   // the same words a user types in chat
  if (style === "scratch") m += " แบบเริ่มจากศูนย์: เลือกเทคที่ดีที่สุดของแต่ละประโยค ตัดช่วงเงียบ ใส่ซับไทยตามเสียงพูดใต้หน้า ไม่ใส่การ์ด ภาพประกอบ เสียงเอฟเฟกต์ เพลง หรือโลโก้ นอกจากที่ผู้ใช้ขอ";
  else if (style && style !== "clubgig") m += ` ให้เป็นสไตล์ ${String(style).replace(/\s+/g, " ").slice(0, 120)}`;   // e.g. "ClubGig + แผนที่เส้นทาง (Route maps)"
  if (auds.length) m += `\nใช้ไฟล์เสียงนี้ด้วย: ${auds.join(" ")}`;
  // 11-09: "Font ของ <a clinic>" made the editor warn that the clip never mentions that clinic: a brand here is theirs
  if (wish) m += `\nผู้ใช้อยากได้: "${String(wish).replace(/\s+/g, " ").slice(0, 300)}" (ชื่อแบรนด์ในนี้คือแบรนด์ของคลิป ไม่ใช่เนื้อหา ไม่ต้องเตือนว่าคลิปไม่พูดถึง)`;
  // a batch: nobody is watching each preview, so the editor checks its own sheet and makes the final (11-09 evening run:
  // "อนุมัติเอง (ผู้ใช้ขอไม่ให้ถาม)" already works that way); changes come later, per clip, from the finished list
  if (batch) m += `\nผู้ใช้สั่งตัดหลายคลิปต่อกัน: ไม่ต้องหยุดรอให้ผู้ใช้ OK คลิปตัวอย่าง ตรวจแผ่นภาพเองแล้วทำไฟล์จริงจนเสร็จ`;
  return m + `\n\n(ส่งมาจากแอป TadClip: ผู้ใช้ตอบระหว่างทางไม่ได้ ตัดสินใจเองจนได้คลิปตัวอย่าง เก็บงานไว้ในโฟลเดอร์ ${DIR}/<ชื่อคลิป> ` +
    `จบทุกครั้งด้วยสรุปภาษาไทยง่ายๆ 2-3 บรรทัด ไม่มีศัพท์เทคนิค ` +
    `บอกสิ่งที่ผู้ใช้ต้องดูเองก่อนโพสต์ไว้บรรทัดสุดท้าย)`;
}

async function turn(text, resume) {
  const bin = claudeBin();
  if (!REPLAY) {
    if (!bin) return fail("no_claude");
    if (!(await online())) return fail("no_net");
    if (!(await signedIn(bin))) return fail("signed_out");
  }
  log("turn", resume ? "resume" : "new", `job=${job.id}`, `bin=${REPLAY ? "replay" : bin}`, JSON.stringify(text.split("\n")[0].slice(0, 120)));
  Object.assign(job, { status: "running", error: null, limit: false, resumeAt: null, turnStarted: Date.now(), result: "", said: [...(job.said || []), text] });
  save();
  const out = fs.createWriteStream(path.join(STATE, `${job.id}.stream.jsonl`), { flags: "a" });
  const args = ["-p", text, "--output-format", "stream-json", "--verbose", "--permission-mode", "dontAsk",
    "--permission-prompts", "none", "--allowedTools", TOOLS, "--add-dir", DIR];
  if (resume) args.push("--resume", job.session);
  child = REPLAY ? spawn(process.execPath, [path.join(APP, "replay.mjs"), REPLAY, DIR, job.files.find((f) => VIDEO.test(f)), text], { cwd: DIR })
    : spawn(bin, args, { cwd: DIR, env: { ...process.env, PATH: PATHX } });
  spawn("caffeinate", ["-i", "-w", String(child.pid)]).on("error", () => {});   // no idle sleep while it works
  let buf = "";
  // Claude that prints nothing in its first 2 min never started (seen 11-09: a user hook stalls it under launchd)
  const quiet = setTimeout(() => { if (child && job.status === "running") { job.error = "stuck"; log("watchdog", `job=${job.id}`, "no output in the first minutes"); child.kill(); } }, +(process.env.TADCLIP_START_MS || 120000));
  child.stdout.on("data", (d) => {
    clearTimeout(quiet);
    out.write(d); buf += d;
    for (let i; (i = buf.indexOf("\n")) >= 0; buf = buf.slice(i + 1)) {
      let e; try { e = JSON.parse(buf.slice(0, i)); } catch { continue; }
      if (e.session_id) job.session = e.session_id;
      const w = e.type === "rate_limit_event" && e.rate_limit_info?.unifiedWindows?.five_hour;
      if (w && typeof w.utilization === "number") { usage = { five: w.utilization, resetsAt: w.resetsAt * 1000, week: e.rate_limit_info.unifiedWindows.seven_day?.utilization ?? null, t: Date.now() }; fs.writeFileSync(USAGE, JSON.stringify(usage)); }
      if (e.type === "result") { Object.assign(job, { result: e.result || "", isError: !!e.is_error });
        log("result", `job=${job.id}`, `error=${!!e.is_error}`, `turns=${e.num_turns}`, `ms=${e.duration_ms}`, `usd=${e.total_cost_usd}`, e.api_error || "", JSON.stringify(String(e.result || "").slice(0, 160))); }
      if (e.type === "result" && e.api_error === "usage_limit_reached") job.limit = true;   // 11-09: the 5-hour limit looked like a crash
    }
  });
  child.stderr.on("data", (d) => out.write(d));
  child.on("error", () => fail("no_claude"));
  child.on("exit", (code) => {
    child = null; out.end();
    log("exit", `job=${job.id}`, `code=${code}`, `secs=${Math.round((Date.now() - job.turnStarted) / 1000)}`);
    clearTimeout(quiet);
    if (job.status !== "running") return;   // stopped by the user
    if (job.error === "stuck") return fail("stuck");
    const after = job.turnStarted - 2000;
    // the final: the file the editor's summary tells them to post, if it's in the folder; else the newest master
    // (11-09 test: the summary named "IMG_2260 (preview).mp4", a copy outside finals/, and it was taken for the final)
    const named = (job.result.match(/`([^`]+\.mp4)`/g) || []).map((x) => x.slice(1, -1))
      .filter((f) => inside(DIR, path.relative(DIR, f)) && fs.existsSync(f) && fs.statSync(f).mtimeMs >= after);
    const final = named.find((f) => !/\((preview|no music)\)/.test(f)) || newest(["finals", /^(?!\.)(?!.*\((preview|no music)).*\.mp4$/, after]);
    const prev = named.find((f) => /\(preview\)\.mp4$/.test(f)) || newest(["finals", /\(preview\)\.mp4$/, after]);
    if (/login|log in|auth|API key/i.test(job.result) && job.isError) return fail("signed_out");
    if (job.limit) { job.resumeAt = (usage?.resetsAt > Date.now() ? usage.resetsAt : Date.now() + 30 * 60000) + PAD; log("limit", `job=${job.id}`, `resume=${new Date(job.resumeAt).toISOString()}`); return fail("limit"); }
    if (code !== 0 || job.isError) return fail("crashed");
    if (final && final !== prev && (!prev || fs.statSync(final).mtimeMs >= fs.statSync(prev).mtimeMs)) Object.assign(job, { status: "final", final });
    else if (prev) Object.assign(job, { status: "preview", preview: prev });
    else job.status = "question";   // it stopped to ask something: the page shows its words
    save(); log("status", `job=${job.id}`, job.status, job.final || job.preview || "");
    if (job.status !== "question") notify(job.status === "final" ? "ไฟล์จริงเสร็จแล้ว" : "คลิปตัวอย่างพร้อมแล้ว กดดูได้เลย");
  });
}
function fail(code) { job.status = "error"; job.error = code; save(); log("error", `job=${job?.id}`, code); }
function notify(text) { spawn("osascript", ["-e", `display notification "${text}" with title "TadClip" sound name "Glass"`]).on("error", () => {}); }

// the Mac slept if a 5 s tick took over a minute: the run carries on after wake, the page says so once
let tick = Date.now();
setInterval(() => { if (Date.now() - tick > 60000 && job?.status === "running") { job.slept = Date.now(); save(); log("slept", `job=${job.id}`, `gap=${Math.round((Date.now() - tick) / 1000)}s`); } tick = Date.now(); }, 5000);

// folder mode (model A): a new video in the folder starts the cut by itself, once it has stopped growing
const seen = new Map();
setInterval(() => {
  if (settings().ui !== "a" || (job && job.status !== "final")) return;   // one clip at a time: never over a preview awaiting their OK
  for (const f of listFiles()) {
    if (f.kind !== "video" || f.done) continue;
    const prev = seen.get(f.name); seen.set(f.name, f.size);
    if (prev === f.size && !job?.files.includes(f.name)) { start([f.name], "clubgig"); break; }
  }
}, 4000);

function settings() { try { return JSON.parse(fs.readFileSync(path.join(STATE, "settings.json"), "utf8")); } catch { return { ui: "b", lang: "th" }; } }
function listFiles() {
  return fs.readdirSync(DIR, { withFileTypes: true }).filter((d) => d.isFile() && !d.name.startsWith(".") && d.name !== "Icon\r").map((d) => {
    const st = fs.statSync(path.join(DIR, d.name)), base = d.name.replace(/\.[^.]+$/, "");
    return { name: d.name, size: st.size, mtime: st.mtimeMs, kind: VIDEO.test(d.name) ? "video" : AUDIO.test(d.name) ? "audio" : "other",
      done: (() => { try { return fs.readdirSync(path.join(DIR, base, "finals")).some((n) => n.endsWith(".mp4")); } catch { return false; } })() };
  }).sort((a, b) => b.mtime - a.mtime);
}

async function start(files, style, wish = "", batch = false) {
  if (child) return { error: "busy" };
  const vids = files.filter((f) => VIDEO.test(f));
  if (!vids.length) { job = { id: Date.now().toString(36), files, status: "error", error: "bad_file", started: Date.now() }; save(); return job; }
  for (const f of vids) if (!REPLAY && !(await probe(path.join(DIR, f)))) {
    job = { id: Date.now().toString(36), files, status: "error", error: "bad_file", bad: f, started: Date.now() }; save(); log("error", "bad_file", JSON.stringify(f)); return job;
  }
  job = { id: Date.now().toString(36), files, style, wish, batch, started: Date.now(), said: [] };
  log("start", `job=${job.id}`, `files=${JSON.stringify(files)}`, `style=${JSON.stringify(style)}`, `wish=${JSON.stringify(wish)}`, `ui=${settings().ui}`);
  turn(message(files, style, wish, batch));
  return job;
}
const carryOn = () => job.session ? turn(job.batch ? "ทำต่อจากที่ค้างไว้ แล้วทำไฟล์จริงจนเสร็จ" : "ทำต่อจากที่ค้างไว้", true) : start(job.files, job.style, job.wish, job.batch);

// every 5 s: a run stopped by the usage limit carries on after the reset; else the next clip in the queue starts, unless
// their own one-off clip is waiting for them (a preview or a question) or the window is too full for another reel
setInterval(() => {
  if (child) return;
  if (job?.status === "error" && job.error === "limit") {
    if (job.resumeAt && Date.now() >= job.resumeAt) { log("resume", `job=${job.id}`, "usage window reset"); carryOn(); }
    return;
  }
  if (!queue.length || (job && !job.batch && job.status !== "final") || job?.status === "running" || paceUntil()) return;
  const it = queue.shift(); saveQ(); log("queue", "next", JSON.stringify(it.files), `left=${queue.length}`);
  start(it.files, it.style, it.wish, true);
}, +(process.env.TADCLIP_QUEUE_MS || 5000));

// ---- http ----
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
  ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".mp4": "video/mp4", ".mov": "video/quicktime", ".gif": "image/gif" };
const send = (res, code, body, type = "application/json") => { res.writeHead(code, { "content-type": type, "cache-control": "no-store" }); res.end(typeof body === "string" ? body : JSON.stringify(body)); };
const inside = (root, p) => { const f = path.resolve(root, p); return f.startsWith(path.resolve(root) + path.sep) ? f : ""; };

function file(req, res, f) {
  let st; try { st = fs.statSync(f); } catch { return send(res, 404, { error: "not found" }); }
  const type = types[path.extname(f).toLowerCase()] || "application/octet-stream";
  const m = /bytes=(\d*)-(\d*)/.exec(req.headers.range || "");
  // !st.size: an empty file (still copying in) asked for by range crashed the whole server (end = -1): send it whole
  if (!m || !st.size) { res.writeHead(200, { "content-type": type, "content-length": st.size, "accept-ranges": "bytes" }); return fs.createReadStream(f).pipe(res); }
  const a = m[1] ? +m[1] : 0, b = m[2] ? +m[2] : st.size - 1;
  res.writeHead(206, { "content-type": type, "content-range": `bytes ${a}-${b}/${st.size}`, "content-length": b - a + 1, "accept-ranges": "bytes" });
  fs.createReadStream(f, { start: a, end: b }).pipe(res);
}
const body = (req) => new Promise((ok) => { let s = ""; req.on("data", (d) => (s += d)); req.on("end", () => { try { ok(JSON.parse(s || "{}")); } catch { ok({}); } }); });

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`), p = decodeURIComponent(url.pathname);
  // only this page may drive it: a web page elsewhere could otherwise send words to an agent that can run commands
  if (!/^(127\.0\.0\.1|localhost):\d+$/.test(req.headers.host || "")) return send(res, 403, { error: "host" });
  if (req.method !== "GET" && req.headers.origin !== `http://${req.headers.host}`) return send(res, 403, { error: "origin" });

  if (p === "/api/state") {
    const s = settings();
    const net = REPLAY ? true : await online();
    const b = await brand(), k = b.kit, bin = claudeBin();
    const signed = REPLAY ? testSignedIn : bin ? await signedIn(bin, false) : null;
    return send(res, 200, { folder: DIR, ui: s.ui, lang: s.lang, files: listFiles(), net, claude: !!bin || !!REPLAY, signedIn: signed, brandId: b.id,
      brand: k && { error: k.error, name: k.name, logo: k.logo && "/media/brand/" + k.logo.file.split("/").map(encodeURIComponent).join("/"), impact: k.impact, font: k.font, fontName: k.font_name,
        colors: k.colors, notes: k.notes, notes_en: k.notes_en, have: k.have, files: k.files, why: k.why, typed: k.typed, avoid: k.avoid,
        proof: k.proof && { video: "/media/brand/" + k.proof.video + "?" + b.id, card: "/media/brand/" + k.proof.card + "?" + b.id } },
      brands: brandNames(), queue: queue.map((i) => i.files.find((f) => VIDEO.test(f))), done: history(),
      waitUntil: (job?.status === "error" && job.error === "limit" && job.resumeAt) || (queue.length && paceUntil()) || 0,
      job: job && { ...job, ...(job.status === "running" ? progress() : { lines: progress().lines }),
        preview: job.preview && "/media/" + path.relative(DIR, job.preview), final: job.final && "/media/" + path.relative(DIR, job.final) } });
  }
  if (req.method === "POST" && p === "/api/start") { const b = await body(req); return send(res, 200, await start(b.files || [], b.style || "clubgig", String(b.wish || "").slice(0, 300))); }
  if (req.method === "POST" && p === "/api/queue") {   // several clips, each its own reel, one after another
    const b = await body(req), files = (b.files || []).map(String), auds = files.filter((f) => AUDIO.test(f));
    const items = files.filter((f) => VIDEO.test(f) && fs.existsSync(path.join(DIR, path.basename(f)))).map((f) => ({ files: [f, ...auds], style: b.style || "clubgig", wish: String(b.wish || "").slice(0, 300) }));
    queue.push(...items); saveQ(); log("queue", "add", items.length, JSON.stringify(items.map((i) => i.files[0])));
    return send(res, 200, { queued: items.length });
  }
  if (req.method === "POST" && p === "/api/pick") {   // open a finished (or failed) job again: its preview/final, and changes resume its session
    const b = await body(req), f = path.join(JOBS, `${String(b.id || "").replace(/[^a-z0-9]/gi, "")}.json`);
    // not while a reel waits out the usage limit: swapping it out would drop its carry-on
    if (child || (job?.status === "error" && job.error === "limit") || !fs.existsSync(f)) return send(res, 409, { error: "busy" });
    job = JSON.parse(fs.readFileSync(f, "utf8")); fs.writeFileSync(JOB, JSON.stringify(job, null, 1)); log("pick", `job=${job.id}`, job.status);
    return send(res, 200, {});
  }
  if (req.method === "POST" && p === "/api/reply") {   // a change after the preview, OK, or an answer to its question
    const b = await body(req);
    if (!job?.session || child) return send(res, 409, { error: "busy" });
    log("reply", `job=${job.id}`, JSON.stringify(String(b.text || "").slice(0, 120)));
    turn(String(b.text || "").slice(0, 500), true);
    return send(res, 200, job);
  }
  if (req.method === "POST" && p === "/api/retry") { log("retry", `job=${job?.id}`, job?.error || job?.status); if (job && !child) carryOn(); return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/stop") {   // stopping a change keeps the preview they already had
    if (child) { job.status = job.preview && fs.existsSync(job.preview) ? "preview" : "stopped"; save(); log("stop", `job=${job.id}`, `back to ${job.status}`); child.kill(); }
    if (job?.batch && queue.length) { log("queue", "cleared by stop", queue.length); queue = []; saveQ(); }   // stop means stop, not "next clip"
    return send(res, 200, {});
  }
  if (req.method === "POST" && p === "/api/new") { if (!child) { log("new", `was=${job?.id}`, job?.status); job = null; fs.rmSync(JOB, { force: true }); } return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/guide") {   // the spotlight guide's steps: shown / next / skip / close / restart, for drop-off per step
    const b = await body(req); log("guide", String(b.step || "").replace(/[^a-z]/g, "").slice(0, 12), String(b.act || "").replace(/[^a-z]/g, "").slice(0, 8));
    return send(res, 200, {});
  }
  if (req.method === "POST" && p === "/api/settings") { const b = await body(req); if (b.ui && b.ui !== settings().ui) log("model", b.ui); fs.writeFileSync(path.join(STATE, "settings.json"), JSON.stringify({ ...settings(), ...b })); return send(res, 200, settings()); }
  // sign-in (11-09 test): the desktop app's sign-in doesn't reach its bundled claude, and auth login wants a real terminal,
  // so a Terminal window runs it; the waiting job starts by itself once auth status says yes
  if (req.method === "POST" && p === "/api/signin") {
    const bin = claudeBin(); if (!bin) return send(res, 200, { error: "no_claude" });
    const cmd = path.join(STATE, "signin.command"), q = (x) => `'${x.replace(/'/g, `'\\''`)}'`;
    fs.writeFileSync(cmd, `#!/bin/bash\nclear\necho "เข้าสู่ระบบ Claude ให้ TadClip (ครั้งเดียว) · Sign in to Claude for TadClip (once)"\necho\n${q(bin)} auth login\n` +
      `echo; echo "เสร็จแล้ว ปิดหน้าต่างนี้ได้ TadClip จะเริ่มตัดต่อเอง · Done: close this window, TadClip starts by itself"\n`, { mode: 0o755 });
    spawn("open", ["-a", "Terminal", cmd]); log("signin", "opened Terminal");
    const t0 = Date.now(), wait = setInterval(async () => {
      if (Date.now() - t0 > 15 * 60000) return clearInterval(wait);
      if (!(await signedIn(bin))) return;
      clearInterval(wait); log("signin", "signed in");   // the page's start button comes back on its next look (auth cache is fresh)
      if (job?.status === "error" && job.error === "signed_out" && !child) { job.session ? turn("ทำต่อจากที่ค้างไว้", true) : start(job.files, job.style, job.wish); }
    }, 3000);
    return send(res, 200, {});
  }
  if (p === "/brandfont") {   // the sample on the page in their font: a file they dropped, else the bundled Thai font they named
    const k = brandCache.kit, own = k?.font === "Brandfont" && Object.keys(k.files || {}).find((f) => k.files[f] === "font");
    const lib = k?.font && path.join(APP, "..", "library", "fonts", "thai", `${k.font.toLowerCase().replace(/ /g, "-")}-thai.woff2`);
    return own ? file(req, res, path.join(BRAND, own)) : lib && fs.existsSync(lib) ? file(req, res, lib) : send(res, 404, {});
  }
  if (req.method === "POST" && p === "/api/open" && url.searchParams.get("what") === "brand") { spawn("open", [BRAND]); log("open", "brand folder"); return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/open") { spawn("open", [url.searchParams.get("what") === "final" && job?.final ? "-R" : "", job?.final || DIR].filter(Boolean)); return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/brandtxt") {   // the page's brand fields -> brand/brand.txt (the loader reads it as before)
    const b = await body(req), lines = TXT.map(([k, th]) => [th, String(b[k] ?? "").replace(/[\r\n]+/g, " ").trim().slice(0, 120)]).filter(([, v]) => v);
    fs.mkdirSync(BRAND, { recursive: true });
    for (const f of own(BRAND)) if (/^(brand|แบรนด์)\.txt$/i.test(f)) fs.rmSync(path.join(BRAND, f));
    if (lines.length) fs.writeFileSync(path.join(BRAND, "brand.txt"), lines.map(([th, v]) => `${th}: ${v}`).join("\n") + "\n");
    log("brand", "fields", JSON.stringify(Object.fromEntries(lines.map(([th, v]) => [th, v.slice(0, 30)]))));
    return send(res, 200, {});
  }
  if (req.method === "POST" && p === "/api/brands") {   // the library: save the brand as <name>, or use a saved one ("" = ClubGig)
    const b = await body(req), name = safeName(b.name);
    if (b.act === "save") { const ok = saveBrand(name); log("brands", "save", JSON.stringify(name), ok); return send(res, ok ? 200 : 400, { ok }); }
    if (b.act === "use") {
      if (name && !brandNames().includes(name)) return send(res, 404, {});
      const cur = brandCache.kit?.name || "แบรนด์ก่อนหน้า";   // never lose the brand in use: it goes to the library first
      if (own(BRAND).length && !brandNames().includes(safeName(cur))) saveBrand(cur);
      for (const f of own(BRAND)) fs.rmSync(path.join(BRAND, f), { recursive: true, force: true });
      fs.rmSync(path.join(BRAND, ".converted"), { recursive: true, force: true });
      if (name) for (const f of own(path.join(BRANDS, name))) fs.copyFileSync(path.join(BRANDS, name, f), path.join(BRAND, f));
      log("brands", "use", JSON.stringify(name || "ClubGig")); return send(res, 200, {});
    }
    return send(res, 400, {});
  }
  if (req.method === "POST" && p === "/api/upload") {   // a clip dropped on the page goes into the folder; a picture, a font or brand.txt into brand/
    let name = path.basename(url.searchParams.get("name") || "");
    if (!name || name.startsWith(".")) return send(res, 400, { error: "name" });
    // 11-09: a dropped page screenshot landed among the clips and counted for nothing until moved by hand. 11-10: every
    // picture, PDF and font a shop has goes to brand/; a slot on the page names its file by role, replacing the last one
    const role = url.searchParams.get("role"), ROLE = { logo: "logo", "logo-light": "logo-white", "logo-dark": "logo-dark", sheet: "brand-sheet", font: "" };
    const to = role in ROLE || /\.(png|jpe?g|webp|heic|heif|svg|pdf|gif|tiff?|bmp|ttf|otf)$/i.test(name) || /^(brand|แบรนด์)\.txt$/i.test(name) ? "brand" : "clips";
    if (to === "brand") {
      fs.mkdirSync(BRAND, { recursive: true });
      if (role in ROLE) {
        const ext = path.extname(name).toLowerCase(), held = Object.entries(brandCache.kit?.files || {}).filter(([, r]) => r === role).map(([f]) => f);
        for (const f of own(BRAND)) if (held.includes(f) || (ROLE[role] && path.parse(f).name === ROLE[role]) || (role === "font" && /\.(ttf|otf)$/i.test(f))) fs.rmSync(path.join(BRAND, f));
        if (ROLE[role]) name = ROLE[role] + ext;
      }
    }
    const out = fs.createWriteStream(path.join(to === "brand" ? BRAND : DIR, name));
    const t0 = Date.now();
    req.pipe(out); out.on("finish", () => { log("upload", JSON.stringify(name), `to=${to}`, role ? `role=${role}` : "", `bytes=${out.bytesWritten}`, `ms=${Date.now() - t0}`); send(res, 200, { name, to }); });
    return;
  }
  if (TEST && req.method === "POST" && p === "/api/test") { const b = await body(req); if ("job" in b) { job = b.job; save(); } if ("signedIn" in b) testSignedIn = !!b.signedIn; return send(res, 200, {}); }
  if (p.startsWith("/media/")) { const f = inside(DIR, p.slice(7)); return f ? file(req, res, f) : send(res, 403, {}); }
  if (p === "/" || p.endsWith(".html")) log("page", p, JSON.stringify((req.headers["user-agent"] || "").replace(/^.*\) /, "").slice(0, 60)));
  const f = inside(path.join(APP, "ui"), p === "/" ? `${settings().ui}.html` : p.slice(1));
  return f ? file(req, res, f) : send(res, 404, {});
});

server.on("error", (e) => {   // already running (the icon was clicked twice): just open the page
  if (e.code === "EADDRINUSE") { if (process.argv.includes("--open")) spawn("open", [`http://127.0.0.1:${PORT}/`]); process.exit(0); }
  throw e;
});
server.listen(PORT, "127.0.0.1", () => {
  console.log(`TadClip app: http://127.0.0.1:${PORT}/  folder ${DIR}${REPLAY ? "  (replay)" : ""}`);
  log("server", `port=${PORT}`, `node=${process.version}`, `claude=${claudeBin() || "none"}`, REPLAY ? "replay" : "", process.argv.includes("--open") ? "opened-page" : "");
  if (process.argv.includes("--open")) spawn("open", [`http://127.0.0.1:${PORT}/`]);
});
