// The spotlight guide (model B): one short step at a time, shown when the user reaches that part of the page. The page
// around the step dims; the part it talks about stays lit and clickable (the dim layer never takes clicks). Each step:
// one sentence, ฟัง reads it aloud, ถัดไป / ข้ามคำแนะนำ, remembered (localStorage) so it resumes where they left off and
// never repeats; "?" in the header starts it again. Every shown / next / skip goes to the app's event log, so a test
// shows where people stop. Why: the 11-09/10 runs lost 10-49 min before the edit started (runs/2026-11-12-onboarding).
const S = {
  // id: [screen, target selector, Thai, English, extra condition]
  clip: ["home", ".files:not(:empty), #drop", "ขั้นแรก: เลือกคลิปที่อยากตัด กดที่คลิป หรือลากคลิปมาวางตรงนี้", "First: choose the clip to edit. Click it, or drop a clip here"],
  style: ["home", ".pair, .styles", "ClubGig คือแบบที่แนะนำ ไม่แน่ใจก็ใช้แบบนี้ได้เลย", "ClubGig is the recommended style. Not sure? Just use it"],
  more: ["home", "[data-act=more]", "อยากลองแบบอื่น กดตรงนี้ มีให้เลือกอีก 18 แบบ", "Want something else? Click here for 18 more styles"],
  wish: ["home", ".wishbox", "อยากได้แบบไหน พิมพ์สั้นๆ หรือกดตัวอย่าง ไม่ใส่ก็ได้", "Want something? Type a few words or click an example. Optional"],
  brand: ["home", ".brandrow", "ใส่โลโก้และสีร้านของคุณได้ ไม่ใส่ก็ได้ จะใช้แบบ ClubGig", "Add your logo and colours here. Optional: without them it uses ClubGig"],
  batch: ["home", "[data-act=batch]", "ถ้าเลือกหลายคลิป กดปุ่มนี้ จะได้คลิปแยกกันครบทุกคลิป", "Several clips? This makes each one its own reel"],
  signin: ["home", "[data-act=signin]", "ก่อนเริ่ม กดปุ่มนี้เข้าสู่ระบบ Claude ครั้งเดียว", "First, press this to sign in to Claude, once"],
  start: ["home", "[data-act=go]", "พร้อมแล้วกดปุ่มนี้ TadClip ตัดต่อให้เอง ประมาณ 30-60 นาที", "Ready? Press this. TadClip edits it for you in about 30-60 minutes"],
  wait: ["running", ".wait .ring", "กำลังตัดต่อ ปิดหน้านี้ได้ เสร็จแล้วจะมีเสียงเตือน", "Editing now. You can close this page; you'll hear a sound when it's done"],
  change: ["preview", ".chips", "ดูคลิปตัวอย่างก่อน อยากแก้ตรงไหน กดปุ่มเหล่านี้", "Watch the preview first. Want a change? Click one of these"],
  ok: ["preview", "[data-act=ok]", "พอใจแล้วกดปุ่มนี้ ได้ไฟล์จริงไว้โพสต์", "Happy with it? Press this for the file you post"],
  final: ["final", "[data-act=show]", "ไฟล์จริงอยู่ในโฟลเดอร์นี้ ส่งเข้ามือถือแล้วโพสต์ได้เลย", "Your file is in this folder. Send it to your phone and post it"],
};
const ORDER = Object.keys(S);
const KEY = "tcGuide";
const load = () => { try { return JSON.parse(localStorage[KEY]) || { done: [] }; } catch { return { done: [] }; } };
const save = (g) => (localStorage[KEY] = JSON.stringify(g));
const log = (step, act) => fetch("/api/guide", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ step, act }) }).catch(() => {});
const W = { th: { next: "ถัดไป", last: "เข้าใจแล้ว", skip: "ข้ามคำแนะนำ", listen: "ฟัง", label: "คำแนะนำ", of: (a, b) => `${a}/${b}` },
  en: { next: "Next", last: "Got it", skip: "Skip tips", listen: "Listen", label: "Tip", of: (a, b) => `${a} of ${b}` } };

let cur = null, lang = "th", shownLang = "", screen = "", hole, box, live;
const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const visible = (el) => el && el.getClientRects().length && getComputedStyle(el).visibility !== "hidden" && !el.closest("[hidden]");
// selectors in the order written: the first that is on screen wins (the clip list before the drop zone)
const target = (id) => S[id][1].split(",").map((q) => [...document.querySelectorAll(q.trim())].find(visible)).find(Boolean);

function build() {
  hole = Object.assign(document.createElement("div"), { className: "gd-hole" }); hole.setAttribute("aria-hidden", "true");
  box = Object.assign(document.createElement("div"), { className: "gd-box" });
  box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "false");
  live = Object.assign(document.createElement("div"), { className: "sr" }); live.setAttribute("aria-live", "polite");
  document.body.append(hole, box, live);
  box.addEventListener("click", (e) => { const a = e.target.closest("[data-gd]")?.dataset.gd; if (a) act(a); });
  addEventListener("keydown", (e) => { if (e.key === "Escape" && cur) act("close"); });
  addEventListener("resize", place); addEventListener("scroll", place, { passive: true });
}
function hide() { cur = null; hole.hidden = box.hidden = true; }
function place() {
  if (!cur) return;
  const el = target(cur); if (!el) return hide();
  const r = el.getBoundingClientRect(), pad = 6;
  Object.assign(hole.style, { top: `${r.top - pad}px`, left: `${r.left - pad}px`, width: `${r.width + 2 * pad}px`, height: `${r.height + 2 * pad}px` });
  // the tip goes where there is more room, above or below, never on the thing it points at
  const bh = box.offsetHeight, bw = box.offsetWidth, below = innerHeight - r.bottom, gap = 14;
  const top = below >= bh + gap + pad || below >= r.top ? Math.min(r.bottom + pad + gap, innerHeight - bh - 8) : Math.max(8, r.top - pad - gap - bh);
  const left = Math.min(Math.max(8, r.left + r.width / 2 - bw / 2), innerWidth - bw - 8);
  Object.assign(box.style, { top: `${top}px`, left: `${left}px` });
  box.dataset.side = top > r.top ? "below" : "above";
}
// "2/7": counted on this screen only, among the steps that apply here now (batch needs 2+ clips, sign-in only when
// signed out), so no number is ever skipped; one step alone shows no count. Re-counted on every render (a 2nd clip adds one)
function count(id) {
  const g = load(), here = ORDER.filter((x) => S[x][0] === screen && (x === id || g.done.includes(x) || target(x)));
  return here.length > 1 ? W[lang].of(here.indexOf(id) + 1, here.length) : "";
}
function show(id, quiet) {
  const w = W[lang], isLast = !next(id);
  cur = id; shownLang = lang; hole.hidden = box.hidden = false; box.setAttribute("aria-label", w.label);
  box.innerHTML = `<p class="gd-n">${count(id)}</p><p class="gd-t">${S[id][lang === "th" ? 2 : 3]}</p>
    <div class="gd-a"><button class="btn ghost small" data-gd="say">${w.listen}</button><button class="btn ghost small" data-gd="skip">${w.skip}</button>
    <button class="btn primary small" data-gd="next">${isLast ? w.last : w.next}</button></div>`;
  const el = target(id);
  if (el) { const r = el.getBoundingClientRect(); if (r.top < 70 || r.bottom > innerHeight - 140) el.scrollIntoView({ block: "center", behavior: still() ? "auto" : "smooth" }); }
  requestAnimationFrame(() => { place(); setTimeout(place, still() ? 0 : 400); });
  if (quiet) return;   // a language switch: same step, new words, not a new "shown"
  live.textContent = S[id][lang === "th" ? 2 : 3];
  // keyboard: the tip's button takes focus only when nothing else has it (never steals from a box being typed in)
  if (!document.activeElement || document.activeElement === document.body) box.querySelector("[data-gd=next]").focus({ preventScroll: true });
  log(id, "shown");
}
// the next step (after `after`, in order) not done yet, on this screen, with something on the page to point at
function next(after) {
  const g = load(); if (g.off) return null;
  return ORDER.slice(after ? ORDER.indexOf(after) + 1 : 0).find((id) => !g.done.includes(id) && S[id][0] === screen && target(id)) || null;
}
function act(a) {
  if (!cur) return;
  const g = load(), id = cur;
  if (a === "say") return say(S[id][lang === "th" ? 2 : 3]);
  if (a === "skip") { g.off = true; save(g); log(id, "skip"); return hide(); }
  g.done = [...new Set([...g.done, id])]; save(g); log(id, a === "close" ? "close" : "next");
  const n = next(id); n ? show(n) : hide();
}
function say(text) {
  const sy = window.speechSynthesis; if (!sy) return; sy.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = lang === "th" ? "th-TH" : "en-US";
  u.voice = sy.getVoices().find((v) => v.lang.replace("_", "-").startsWith(u.lang)) || null; u.rate = 0.9; sy.speak(u);
}
// after every render: keep the current tip on its (re-drawn) target, or start the next one for this screen
export function guide(scr, l) {
  if (!hole) build();
  lang = l; screen = scr;
  if (cur && S[cur][0] === scr && target(cur)) { if (lang !== shownLang) return show(cur, true); box.querySelector(".gd-n").textContent = count(cur); return place(); }
  hide(); const n = next(null); if (n) show(n);
}
export function restart() { localStorage.removeItem(KEY); log("all", "restart"); hide(); }
export const GUIDE_STEPS = ORDER;
