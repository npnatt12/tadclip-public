// node shot.mjs <url> <out.png> [w] [h] [dark]: one screenshot, for looking at a screen
import { chromium } from "playwright";
const [url, out, w = 1280, h = 900, dark] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h }, colorScheme: dark ? "dark" : "light" });
await p.goto(url); await p.waitForTimeout(1200); await p.screenshot({ path: out, fullPage: true }); await b.close();
