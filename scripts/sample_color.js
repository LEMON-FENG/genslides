/* genslides · pixel-sample the average dark-text color of a region in a rendered image.
 * Use to settle title color (black vs navy) when XML inheritance is ambiguous.
 * Usage: NODE_PATH=<env.nodeModules> node sample_color.js <image> [left%] [top%] [w%] [h%]
 *   defaults sample the top-left title strip: 3.5% 3% 45% 5%
 */
const sharp = require("sharp");
(async () => {
  const f = process.argv[2];
  if (!f) { console.error("usage: node sample_color.js <image> [left% top% w% h%]"); process.exit(2); }
  const L = +(process.argv[3] ?? 0.035), Tp = +(process.argv[4] ?? 0.03), Wp = +(process.argv[5] ?? 0.45), Hp = +(process.argv[6] ?? 0.05);
  const meta = await sharp(f).metadata();
  const left = Math.round(meta.width * L), top = Math.round(meta.height * Tp);
  const w = Math.round(meta.width * Wp), h = Math.round(meta.height * Hp);
  const { data, info } = await sharp(f).extract({ left, top, width: w, height: h }).raw().toBuffer({ resolveWithObject: true });
  let r = 0, g = 0, b = 0, n = 0;
  for (let i = 0; i < data.length; i += info.channels) {
    const R = data[i], G = data[i + 1], B = data[i + 2];
    if (R + G + B < 160) { r += R; g += G; b += B; n++; } // dark (text) pixels only
  }
  const hex = (x) => Math.round(x).toString(16).padStart(2, "0").toUpperCase();
  if (!n) { console.log("no dark pixels in region"); return; }
  console.log("avg dark text:", "#" + hex(r / n) + hex(g / n) + hex(b / n), `(rgb ${Math.round(r/n)},${Math.round(g/n)},${Math.round(b/n)}, n=${n})`);
})();
