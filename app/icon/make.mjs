// node app/icon/make.mjs: renders icon.html to icon-1024.png (the .app and folder icon) and ../ui/icon.png (the page's favicon)
import { chromium } from "../test/node_modules/playwright/index.mjs";
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } });
await p.goto(new URL("./icon.html", import.meta.url).href); await p.waitForTimeout(300);
await p.locator(".i").screenshot({ path: new URL("./icon-1024.png", import.meta.url).pathname, omitBackground: true });
await b.close();
