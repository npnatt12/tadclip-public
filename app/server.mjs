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
const REPLAY = process.env.TADCLIP_REPLAY || "";
const TEST = process.env.TADCLIP_TEST === "1";   // lets the checks force any error screen
const PATHX = [`${HOME}/.local/bin`, "/opt/homebrew/opt/node@22/bin", "/opt/homebrew/bin", "/usr/local/bin", process.env.PATH].join(":");
const VIDEO = /\.(mov|mp4|m4v|avi|mkv|mts|3gp|hevc|webm)$/i, AUDIO = /\.(mp3|m4a|wav|aac|aif|aiff|flac|ogg)$/i;
const TOOLS = "Bash,Read,Write,Edit,Glob,Grep,Agent,Skill,TodoWrite";
fs.mkdirSync(STATE, { recursive: true });
// one timestamped line per event, for test runs and bug reports (scripts/logs.sh collects it)
const EV = path.join(STATE, "events.log");
const log = (...a) => fs.appendFileSync(EV, `${new Date().toISOString()} ${a.join(" ")}\n`);

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
async function signedIn(bin) {
  const r = await run(bin, ["auth", "status"]);
  try { return JSON.parse(r.out).loggedIn === true; } catch { return r.code === 0; }
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
const save = () => fs.writeFileSync(JOB, JSON.stringify(job, null, 1));
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

function message(files, style) {
  const vids = files.filter((f) => VIDEO.test(f)).map((f) => path.join(DIR, f));
  const auds = files.filter((f) => AUDIO.test(f)).map((f) => path.join(DIR, f));
  let m = `ตัดต่อคลิปนี้ ${vids.join(" ")}`;   // the same words a user types in chat
  if (style && style !== "clubgig") m += ` ให้เป็นสไตล์ ${String(style).replace(/\s+/g, " ").slice(0, 120)}`;   // e.g. "ClubGig + แผนที่เส้นทาง (Route maps)"
  if (auds.length) m += `\nใช้ไฟล์เสียงนี้ด้วย: ${auds.join(" ")}`;
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
  Object.assign(job, { status: "running", error: null, turnStarted: Date.now(), result: "", said: [...(job.said || []), text] });
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
    const named = (job.result.match(/`([^`]+\.mp4)`/g) || []).map((x) => x.slice(1, -1)).find((f) => inside(DIR, path.relative(DIR, f)) && fs.existsSync(f));
    const final = named && fs.statSync(named).mtimeMs >= after ? named : newest(["finals", /^(?!.*\((preview|no music)).*\.mp4$/, after]);
    const prev = newest(["finals", /\(preview\)\.mp4$/, after]);
    if (/login|log in|auth|API key/i.test(job.result) && job.isError) return fail("signed_out");
    if (job.limit) return fail("limit");
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

async function start(files, style) {
  if (child) return { error: "busy" };
  const vids = files.filter((f) => VIDEO.test(f));
  if (!vids.length) { job = { id: Date.now().toString(36), files, status: "error", error: "bad_file", started: Date.now() }; save(); return job; }
  for (const f of vids) if (!REPLAY && !(await probe(path.join(DIR, f)))) {
    job = { id: Date.now().toString(36), files, status: "error", error: "bad_file", bad: f, started: Date.now() }; save(); log("error", "bad_file", JSON.stringify(f)); return job;
  }
  job = { id: Date.now().toString(36), files, style, started: Date.now(), said: [] };
  log("start", `job=${job.id}`, `files=${JSON.stringify(files)}`, `style=${JSON.stringify(style)}`, `ui=${settings().ui}`);
  turn(message(files, style));
  return job;
}

// ---- http ----
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
  ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".mp4": "video/mp4", ".mov": "video/quicktime", ".gif": "image/gif" };
const send = (res, code, body, type = "application/json") => { res.writeHead(code, { "content-type": type, "cache-control": "no-store" }); res.end(typeof body === "string" ? body : JSON.stringify(body)); };
const inside = (root, p) => { const f = path.resolve(root, p); return f.startsWith(path.resolve(root) + path.sep) ? f : ""; };

function file(req, res, f) {
  let st; try { st = fs.statSync(f); } catch { return send(res, 404, { error: "not found" }); }
  const type = types[path.extname(f).toLowerCase()] || "application/octet-stream";
  const m = /bytes=(\d*)-(\d*)/.exec(req.headers.range || "");
  if (!m) { res.writeHead(200, { "content-type": type, "content-length": st.size, "accept-ranges": "bytes" }); return fs.createReadStream(f).pipe(res); }
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
    return send(res, 200, { folder: DIR, ui: s.ui, lang: s.lang, files: listFiles(), net, claude: !!claudeBin() || !!REPLAY,
      job: job && { ...job, ...(job.status === "running" ? progress() : { lines: progress().lines }),
        preview: job.preview && "/media/" + path.relative(DIR, job.preview), final: job.final && "/media/" + path.relative(DIR, job.final) } });
  }
  if (req.method === "POST" && p === "/api/start") { const b = await body(req); return send(res, 200, await start(b.files || [], b.style || "clubgig")); }
  if (req.method === "POST" && p === "/api/reply") {   // a change after the preview, OK, or an answer to its question
    const b = await body(req);
    if (!job?.session || child) return send(res, 409, { error: "busy" });
    log("reply", `job=${job.id}`, JSON.stringify(String(b.text || "").slice(0, 120)));
    turn(String(b.text || "").slice(0, 500), true);
    return send(res, 200, job);
  }
  if (req.method === "POST" && p === "/api/retry") { log("retry", `job=${job?.id}`, job?.error || job?.status); if (job && !child) { job.session ? turn("ทำต่อจากที่ค้างไว้", true) : start(job.files, job.style); } return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/stop") {   // stopping a change keeps the preview they already had
    if (child) { job.status = job.preview && fs.existsSync(job.preview) ? "preview" : "stopped"; save(); log("stop", `job=${job.id}`, `back to ${job.status}`); child.kill(); }
    return send(res, 200, {});
  }
  if (req.method === "POST" && p === "/api/new") { if (!child) { log("new", `was=${job?.id}`, job?.status); job = null; fs.rmSync(JOB, { force: true }); } return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/settings") { const b = await body(req); if (b.ui && b.ui !== settings().ui) log("model", b.ui); fs.writeFileSync(path.join(STATE, "settings.json"), JSON.stringify({ ...settings(), ...b })); return send(res, 200, settings()); }
  if (req.method === "POST" && p === "/api/open") { spawn("open", [url.searchParams.get("what") === "final" && job?.final ? "-R" : "", job?.final || DIR].filter(Boolean)); return send(res, 200, {}); }
  if (req.method === "POST" && p === "/api/upload") {   // a file dropped on the page goes into the folder
    const name = path.basename(url.searchParams.get("name") || "");
    if (!name || name.startsWith(".")) return send(res, 400, { error: "name" });
    const out = fs.createWriteStream(path.join(DIR, name));
    const t0 = Date.now();
    req.pipe(out); out.on("finish", () => { log("upload", JSON.stringify(name), `bytes=${out.bytesWritten}`, `ms=${Date.now() - t0}`); send(res, 200, { name }); });
    return;
  }
  if (TEST && req.method === "POST" && p === "/api/test") { const b = await body(req); job = b.job; save(); return send(res, 200, {}); }
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
