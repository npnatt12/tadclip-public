// One real run driven through the page like a user: "ตัดคลิปใหม่", choose the clip with the file picker (uploads into the
// folder), keep ClubGig, press ตัดต่อให้หน่อย. node e2e-live.mjs <clip> [port]
import { chromium } from "playwright";
const [clip, port = 4747] = process.argv.slice(2), U = `http://127.0.0.1:${port}`;
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.goto(`${U}/b.html`); await p.waitForTimeout(2500);
if (await p.locator("[data-act=fresh]:visible").count()) { await p.locator("[data-act=fresh]:visible").first().click(); await p.waitForTimeout(2500); }
const t0 = Date.now();
await p.locator("#pick").setInputFiles(clip);
await p.waitForFunction((n) => [...document.querySelectorAll("[data-file]")].some((e) => e.dataset.file === n && e.getAttribute("aria-pressed") === "true"), clip.split("/").pop(), { timeout: 120000 });
console.log("uploaded + chosen in", Math.round((Date.now() - t0) / 1000), "s");
await p.locator("[data-act=go]").click();
await p.waitForFunction(() => /กำลังตัดต่อ/.test(document.body.innerText), null, { timeout: 60000 });
console.log("waiting screen after", Math.round((Date.now() - t0) / 1000), "s");
await p.screenshot({ path: "e2e-running.png" });
await b.close();
