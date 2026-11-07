// styles/clubgig.json carries only the look (font, colours, framing). The devices live in hand-planned beats, so a reel
// with none of them still builds and looks "ClubGig". This is what a reel must hold before it may render.
// reel.json "omit": ["linecta"] drops a device, only when the user asked. Creator overlays have their own formats: not checked.
export function clubgigMissing(spec, beats, E, speech, sfxHits) {
  const of = (t) => beats.filter((b) => b.type === t), impacts = of("impact"), stock = of("broll");
  const clip = (b) => b.type === "broll" || (b.type === "polaroid" && /\.(mp4|mov|webm)$/i.test(b.src || ""));
  const popups = Math.max(2, Math.floor(speech / 15)); // ponytail: the floor, not KG01's budget (~11 per 90 s)
  const need = {
    hook: ["hook card (impact look qcard within 2 s)", impacts.some((b) => b.look === "qcard" && E(b.at) <= 2)],
    hookStock: ["hook stock (broll or polaroid clip within 2 s)", beats.some((b) => clip(b) && E(b.at) <= 2)],
    impact: [`popups (${impacts.length} impact beats, want >= ${popups})`, impacts.length >= popups],
    swipe: ["swiped stock (broll with swipe)", stock.some((b) => b.swipe)],
    chrome: ["brand chrome (chrome)", !!spec.chrome],
    linecta: ["LINE CTA (linecta)", of("linecta").length > 0],
    endcard: ["end card (endcard)", of("endcard").length > 0],
    sfx: ["sound (0 SFX hits)", sfxHits > 0],
  };
  return Object.entries(need).filter(([k, [, ok]]) => !ok && !(spec.omit || []).includes(k)).map(([, [label]]) => label);
}
