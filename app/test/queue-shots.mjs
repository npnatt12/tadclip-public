// screenshots + axe of the batch screens (home with 3 clips, running with a queue, finished list, limit with a time)
//   server on 4848 in replay mode with TADCLIP_REPLAY_LIMIT=1; node app/test/queue-shots.mjs <out dir>
import { chromium } from "playwright";
import fs from "node:fs";
const BASE = "http://127.0.0.1:4848", OUT = process.argv[2];
const AXE = fs.readFileSync(new URL("./node_modules/axe-core/axe.min.js", import.meta.url), "utf8");
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 900, height: 1100 } });
const axe = async (n) => { await p.addScriptTag({ content: AXE }); const r = await p.evaluate(async () => (await axe.run({ runOnly: ["wcag2a", "wcag2aa"] })).violations.map((v) => v.id)); console.log(n, "axe:", r.join(",") || "none"); };
const shot = async (n) => { await p.screenshot({ path: `${OUT}/${n}.png`, fullPage: true }); await axe(n); };
await p.goto(BASE); await p.waitForTimeout(3000);
for (const n of ["a.mov", "b.mov"]) await p.click(`[data-file="${n}"]`);
await p.waitForTimeout(800); await shot("1-home-batch");
await p.click("[data-act=batch]"); await p.waitForTimeout(4000); await shot("2-limit");
console.log("limit text:", (await p.textContent("section.err")).replace(/\s+/g, " ").trim());
await p.waitForTimeout(16000); await shot("3-running-queue");
await p.waitForTimeout(30000); await shot("4-done");
await b.close();
