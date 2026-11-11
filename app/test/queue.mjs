// The queue and the usage window, end to end through the server in replay mode (no browser, ~1 min):
//   node app/test/queue.mjs
// A: three clips queued run one after another, each to its own final, in order.
// B: when a reel leaves the 5-hour window above the headroom, the next clip waits for the reset, then starts.
// C: a run that hits the usage limit shows the limit screen with a resume time, then carries on by itself.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const APP = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");   // not URL.pathname: "/D:/..." on Windows
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
let port = 4900, bad = 0;
async function scenario(name, env, fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tc-q-")), base = `http://127.0.0.1:${++port}`;
  for (const n of ["a.mov", "b.mov", "c.mov"]) fs.writeFileSync(path.join(dir, n), "x");
  const srv = spawn(process.execPath, [path.join(APP, "server.mjs")], { env: { ...process.env, TADCLIP_PORT: String(port), TADCLIP_DIR: dir,
    TADCLIP_REPLAY: path.join(APP, "test", "fixture"), TADCLIP_REPLAY_SECONDS: "2", TADCLIP_QUEUE_MS: "300", TADCLIP_RESUME_PAD_MS: "0", ...env }, stdio: "ignore" });
  const H = { "content-type": "application/json", origin: base };
  const api = { state: () => fetch(base + "/api/state").then((r) => r.json()), post: (p, b) => fetch(base + p, { method: "POST", headers: H, body: JSON.stringify(b) }).then((r) => r.json()) };
  for (let i = 0; i < 50; i++) { try { await api.state(); break; } catch { await wait(200); } }
  const until = async (pred, ms) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { const s = await api.state(); if (pred(s)) return s; await wait(250); } return null; };
  try { const msg = await fn(api, until, dir, base); console.log(msg ? `FAIL ${name}: ${msg}` : `ok   ${name}`); if (msg) bad = 1; }
  // Windows: the folder stays locked while the server (or its replay child, cwd = the folder) is alive: wait, then retry
  finally { const gone = new Promise((r) => srv.once("exit", r)); srv.kill(); await gone; fs.rmSync(dir, { recursive: true, force: true, maxRetries: 20, retryDelay: 500 }); }
}
const finals = (s) => s.done.filter((d) => d.status === "final");

await scenario("A three clips, in order, each a final", { TADCLIP_REPLAY_USE: "0.2" }, async (api, until) => {
  const r = await api.post("/api/queue", { files: ["a.mov", "b.mov", "c.mov"], style: "clubgig" });
  if (r.queued !== 3) return `queued ${r.queued}`;
  const s = await until((s) => finals(s).length === 3 && !s.queue.length, 40000);
  if (!s) return "not all three finished";
  const order = finals(s).map((d) => d.name).reverse().join(",");
  return order === "a.mov,b.mov,c.mov" && s.done.every((d) => d.batch) ? "" : `order ${order}`;
});

await scenario("B a full window holds the next clip until the reset + pad", { TADCLIP_REPLAY_USE: "0.7", TADCLIP_REPLAY_RESET: "4", TADCLIP_RESUME_PAD_MS: "8000" }, async (api, until) => {
  await api.post("/api/queue", { files: ["a.mov", "b.mov"] });
  const held = await until((s) => finals(s).length === 1 && s.queue.length === 1 && s.waitUntil > Date.now(), 20000);
  if (!held) return "the second clip did not wait";
  await wait(Math.max(0, held.waitUntil - 8000 + 2000 - Date.now()));   // 2 s past the reset itself, still inside the pad
  if ((await api.state()).queue.length !== 1) return "started at the reset, before the pad";
  return (await until((s) => finals(s).length === 2, 30000)) ? "" : "never started after the reset";
});

await scenario("C the usage limit: limit screen with a time, then carries on", { TADCLIP_REPLAY_LIMIT: "1", TADCLIP_REPLAY_RESET: "4" }, async (api, until, dir, base) => {
  await api.post("/api/queue", { files: ["a.mov"] });
  const lim = await until((s) => s.job?.error === "limit", 15000);
  if (!lim) return "no limit screen";
  if (!(lim.job.resumeAt > Date.now() && lim.waitUntil === lim.job.resumeAt)) return `no resume time ${lim.job.resumeAt}`;
  const pick = await fetch(base + "/api/pick", { method: "POST", headers: { "content-type": "application/json", origin: base }, body: JSON.stringify({ id: lim.job.id }) });
  if (pick.status !== 409) return "opening a reel while one waits for the limit was allowed";
  return (await until((s) => s.job?.status === "final", 30000)) ? "" : "did not carry on after the reset";
});
await scenario("D an empty clip still copying in doesn't crash the server", {}, async (api, until, dir, base) => {
  fs.writeFileSync(path.join(dir, "copying.mov"), "");
  const r = await fetch(base + "/media/copying.mov", { headers: { range: "bytes=0-" } });
  await wait(300);
  return r.status === 200 && (await api.state()).files ? "" : `status ${r.status}`;
});
await scenario("E a log that can't be written (full disk) doesn't end the server", {}, async (api, until, dir, base) => {
  const ev = path.join(dir, ".tadclip", "events.log"); fs.rmSync(ev, { force: true }); fs.mkdirSync(ev);   // every append now throws, as on a full disk
  const r = await fetch(base + "/api/new", { method: "POST", headers: { "content-type": "application/json", origin: base }, body: "{}" }).catch(() => null);   // logs a line
  await wait(300);
  const alive = await api.state().then(() => true).catch(() => false);
  return r?.status === 200 && alive ? "" : `status ${r?.status}, server alive ${alive}`;
});
process.exit(bad);
