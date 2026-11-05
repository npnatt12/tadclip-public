// Style presets (styles/<name>.json). Old names keep loading, so reels built before a rename still build.
// "extends": "<style>" layers a preset over another one: a creator style is a small overlay on ClubGig.
import fs from "node:fs";
import path from "node:path";

export const STYLE_ALIAS = { icarus: "clubgig", "icarus-seoul": "clubgig-seoul", "icarus-paper": "clubgig-paper" };
export const styleName = (n) => STYLE_ALIAS[n] ?? n;

export const deepMerge = (a, b) => {
  if (b === undefined) return a;
  if (a && b && typeof a === "object" && typeof b === "object" && !Array.isArray(a) && !Array.isArray(b)) {
    const o = { ...a };
    for (const k of Object.keys(b)) o[k] = deepMerge(a[k], b[k]);
    return o;
  }
  return b;
};

// null when the style does not exist; a broken "extends" throws (a silent gap would render the wrong look)
export function loadStyle(skill, name, seen = []) {
  const n = styleName(name);
  if (seen.includes(n)) throw new Error(`style ${n}: "extends" loops (${[...seen, n].join(" -> ")})`);
  const sp = path.join(skill, "styles", `${n}.json`);
  if (!fs.existsSync(sp)) return null;
  const { extends: base, _about, ...own } = JSON.parse(fs.readFileSync(sp, "utf8"));
  if (!base) return own;
  const parent = loadStyle(skill, base, [...seen, n]);
  if (!parent) throw new Error(`style ${n}: "extends" names unknown style ${base}`);
  return deepMerge(parent, own);
}
