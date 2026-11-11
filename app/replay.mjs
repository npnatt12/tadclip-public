// Stands in for `claude -p` when TADCLIP_REPLAY is set: replays a recorded run so the page can be tested in seconds.
//   node replay.mjs <fixture dir> <TadClip folder> <clip name> <message>
// fixture: progress.log (the real run's lines), stream.jsonl (optional), preview.mp4 (optional: else a plain test clip is made)
// TADCLIP_REPLAY_SECONDS (default 20) is how long the whole run takes; TADCLIP_REPLAY_FAIL=1 exits 1 halfway (a crash);
// TADCLIP_REPLAY_HANG=1 prints nothing (a Claude that never starts).
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const [fx, dir, clip, text = ""] = process.argv.slice(2);
const P = path.join(dir, clip.replace(/\.[^.]+$/, "")), secs = +(process.env.TADCLIP_REPLAY_SECONDS || 20);
fs.mkdirSync(path.join(P, "build"), { recursive: true }); fs.mkdirSync(path.join(P, "finals"), { recursive: true });
const final = /ไฟล์จริง|final/i.test(text);
const lines = final ? ["[1/2] ทำไฟล์จริงความละเอียดเต็ม | full-quality render, ~5 min", "[2/2] ตรวจไฟล์ก่อนส่ง | QA checks, ~2 min"]
  : fs.readFileSync(path.join(fx, "progress.log"), "utf8").trim().split("\n").map((l) => l.replace(/^\d\d:\d\d\s*/, ""));
const log = path.join(P, "build", "progress.log"), wait = (ms) => new Promise((r) => setTimeout(r, ms));
const emit = (e) => process.stdout.write(JSON.stringify({ session_id: "replay-0000", ...e }) + "\n");
if (process.env.TADCLIP_REPLAY_HANG) await wait(600000);   // a Claude that never starts: the server's watchdog must catch it
emit({ type: "system", subtype: "init" });
// Claude's usage meter, as the real stream reports it: TADCLIP_REPLAY_USE (5-hour window share after this run, default 0.2),
// TADCLIP_REPLAY_RESET seconds until the window resets (default 3600); TADCLIP_REPLAY_LIMIT=1 hits the limit on the first
// run in this folder (a marker file), as `claude -p` does when the 5-hour window is used up
const reset = Math.round(Date.now() / 1000) + +(process.env.TADCLIP_REPLAY_RESET || 3600);
const meter = (u) => emit({ type: "rate_limit_event", rate_limit_info: { status: u >= 1 ? "rejected" : "allowed", unifiedWindows: { five_hour: { utilization: u, resetsAt: reset }, seven_day: { utilization: 0.1 } } } });
const mark = path.join(dir, ".tadclip", "replay-limit-hit");
if (process.env.TADCLIP_REPLAY_LIMIT && !fs.existsSync(mark)) {
  fs.writeFileSync(mark, ""); await wait(500); meter(1);
  emit({ type: "result", subtype: "error", is_error: true, api_error: "usage_limit_reached", result: "Claude usage limit reached" }); process.exit(1);
}
for (const [i, l] of lines.entries()) {
  const d = new Date();
  fs.appendFileSync(log, `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")} ${l}\n`);
  if (process.env.TADCLIP_REPLAY_FAIL && i === Math.floor(lines.length / 2)) process.exit(1);
  await wait((secs * 1000) / lines.length);
}
const src = path.join(fx, "preview.mp4"), out = path.join(P, "finals", final ? "TC01 - ClubGig.mp4" : "TC01 - ClubGig (preview).mp4");
if (fs.existsSync(src)) fs.copyFileSync(src, out);
else execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x6A2C3B:s=360x640:d=4", "-f", "lavfi", "-i", "sine=f=440:d=4",
  "-vf", "drawtext=text='TadClip test':fontcolor=white:fontsize=36:x=(w-tw)/2:y=(h-th)/2", "-shortest", "-pix_fmt", "yuv420p", out]);
// like the real 11-09 run: the preview is also copied next to the project and its summary names that copy
const named = path.join(P, `${path.basename(P)}${final ? "" : " (preview)"}.mp4`); fs.copyFileSync(out, named);
meter(+(process.env.TADCLIP_REPLAY_USE || 0.2));
emit({ type: "result", subtype: "success", is_error: false, result: (final ? "ทำไฟล์จริงเสร็จแล้ว" : "ได้คลิปตัวอย่างแล้ว ความยาว 58 วินาที ใช้สไตล์ ClubGig") + ` ไฟล์อยู่ที่ \`${named}\`` });
