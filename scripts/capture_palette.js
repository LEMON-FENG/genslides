/* genslides · capture a brand palette from an image (rendered deck slide / brand screenshot / logo).
 * Frequency-counts colors, filters near-white/near-black/greys, surfaces the saturated brand colors
 * plus light tints — so you can map them into a new config/theme.<brand>.json. NEVER guess brand
 * colors from memory; sample them. (Brand-capture idea borrowed from huashu-design, trimmed.)
 *
 * Usage: NODE_PATH=<env.nodeModules> node capture_palette.js <image> [topN=8]
 */
const sharp = require("sharp");
const hex = (r, g, b) => "#" + [r, g, b].map(x => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, "0")).join("").toUpperCase();
(async () => {
  const f = process.argv[2];
  const topN = parseInt(process.argv[3] || "8", 10);
  if (!f) { console.error("usage: node capture_palette.js <image> [topN]"); process.exit(2); }
  const { data, info } = await sharp(f).resize(240, 240, { fit: "inside" }).raw().toBuffer({ resolveWithObject: true });
  const ch = info.channels, tally = new Map();
  for (let i = 0; i < data.length; i += ch) {
    const r = data[i], g = data[i + 1], b = data[i + 2];
    const q = v => Math.round(v / 16) * 16;                 // quantize to 16-steps
    const key = `${q(r)},${q(g)},${q(b)}`;
    tally.set(key, (tally.get(key) || 0) + 1);
  }
  const rows = [...tally.entries()].map(([k, n]) => {
    const [r, g, b] = k.split(",").map(Number);
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;
    const sat = mx === 0 ? 0 : (mx - mn) / mx;
    return { r, g, b, n, lum, sat, hex: hex(r, g, b) };
  });
  const total = rows.reduce((a, x) => a + x.n, 0);
  // brand colors = saturated, not near-white/black
  const brand = rows.filter(x => x.sat >= 0.12 && x.lum > 20 && x.lum < 245)
    .sort((a, b) => b.n - a.n).slice(0, topN);
  // light tints = bright, low-mid sat, not pure white (paleBg/cardBg candidates)
  const tints = rows.filter(x => x.lum >= 205 && x.lum < 250 && x.sat >= 0.04 && x.sat < 0.45)
    .sort((a, b) => b.n - a.n).slice(0, 4);
  const pct = x => ((x.n / total) * 100).toFixed(1) + "%";
  const guess = (cond) => (brand.filter(cond)[0] || {}).hex || "?";

  console.log("=== brand colors (saturated, by frequency) ===");
  brand.forEach(x => console.log(`  ${x.hex}  ${pct(x).padStart(6)}  lum=${Math.round(x.lum)} sat=${x.sat.toFixed(2)}`));
  console.log("=== light tints (paleBg/cardBg candidates) ===");
  tints.forEach(x => console.log(`  ${x.hex}  ${pct(x).padStart(6)}  lum=${Math.round(x.lum)}`));
  console.log("\n=== heuristic role guess (VERIFY before writing theme.json) ===");
  console.log("  primary (dark brand)  :", guess(x => x.lum <= 95).replace("#", ""));
  console.log("  accent  (bright brand):", guess(x => x.lum > 95 && x.lum < 190).replace("#", ""));
  console.log("  paleBg  (light tint)  :", (tints[0] ? tints[0].hex : "?").replace("#", ""));
  console.log("\nNext: copy config/theme.json → config/theme.<brand>.json, replace palette/title colors with the");
  console.log("verified hexes, then generate with env GENSLIDES_THEME=config/theme.<brand>.json. Default KPMG theme.json is untouched.");
})();
