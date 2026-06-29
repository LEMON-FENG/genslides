/* ============================================================
 * genslides · pptxgenjs house template (default brand: KPMG; configurable)
 *
 * Copy this per page. Reproduce the APPROVED HTML mockup faithfully.
 * Colors/fonts/title come from config/theme.json (single source of truth).
 * Small accents/tiles/badges use a UNIQUE placeholder color (PH.*) →
 * scripts/postprocess.py swaps them to real gradFill. Large areas stay solid.
 *
 * Run:  NODE_PATH=<env.nodeModules> node gen_<page>.js out.pptx
 * Then: python scripts/postprocess.py out.pptx   (fonts + notesMasterIdLst + gradients)
 *       python <env.validatePy> out.pptx          (must PASS)
 *       scripts/render.ps1 out.pptx               (eyeball)  + fresh-eyes QA subagent
 * ============================================================ */
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

// ---- theme (single source of truth) ----
const THEME_PATH = process.env.GENSLIDES_THEME || path.join(__dirname, "..", "config", "theme.json");
const T = JSON.parse(fs.readFileSync(THEME_PATH, "utf8"));
const C = T.palette;
const FF = T.fonts.eastasian;       // pptxgenjs fontFace; postprocess fixes latin/cs slots
const PH = Object.keys(T.gradients.placeholders); // ["EE0001", ...]; use PH[i] or a named map below

// convenience names (edit to taste; all resolve from theme)
const NAVY = C.primary, ACCENT = C.accent, WHITE = C.white;
const BORDER = C.border, INK = C.ink, G66 = C.gray66, G88 = C.gray88;

const PX = (p) => p / 96;           // 1px ≈ 1/96in, for mapping HTML px → inches
const mkShadow = (op = 0.12, blur = 8, off = 3, color = "002A6E") =>
  ({ type: "outer", color, blur, offset: off, angle: 90, opacity: op });

async function iconPng(IconC, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(IconC, { color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
// rough text width (inches) for chip/tag auto-sizing
function estW(s, pt) {
  const u = pt / 72; let w = 0;
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (c >= 0x4e00 && c <= 0x9fff) w += u * 1.0;
    else if ("·，。、；（）⇄→／/".includes(ch)) w += u * 0.92;
    else if (/[A-Z0-9%]/.test(ch)) w += u * 0.6;
    else if (ch === " ") w += u * 0.3;
    else w += u * 0.5;
  }
  return w;
}

(async () => {
  const pres = new pptxgen();
  pres.defineLayout({ name: "W", width: T.layout.widthIn, height: T.layout.heightIn });
  pres.layout = "W";
  pres.author = T.brand.name;
  pres.title = "genslides page";

  const s = pres.addSlide();
  s.background = { color: WHITE };

  const M = T.layout.marginIn, CW = T.layout.widthIn - M * 2;

  // ---- title / subtitle (from theme.title) ----
  const L1 = T.title.level1, L2 = T.title.level2;
  s.addText("主题：阐述（一级主标题 · 冒号式）", {
    x: M, y: 0.18, w: CW, h: 0.46, fontFace: FF, fontSize: L1.size, bold: L1.bold, color: L1.color, margin: 0, valign: "middle",
  });
  s.addText("二级副标题：一句正式商务、单段，说明本页的做法与结果。", {
    x: M, y: 0.66, w: CW, h: 0.3, fontFace: FF, fontSize: L2.size, bold: L2.bold, color: L2.color, margin: 0, valign: "middle",
  });

  // =========================================================
  // EXAMPLE COMPONENTS — replace with the approved mockup's layout
  // =========================================================
  const icon = await iconPng(fa.FaRegFileAlt, "#FFFFFF");

  // (a) card with header strip + left accent bar + icon
  const cardX = M, cardY = 1.2, cardW = 3.6, cardH = 1.6, hdrH = 0.44;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cardX, y: cardY, w: cardW, h: cardH, rectRadius: 0.06, fill: { color: WHITE }, line: { color: BORDER, width: 0.75 }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: cardX, y: cardY, w: cardW, h: hdrH, fill: { color: ACCENT } });
  s.addImage({ data: icon, x: cardX + 0.16, y: cardY + 0.12, w: 0.2, h: 0.2 });
  s.addText("卡片标题", { x: cardX + 0.46, y: cardY, w: cardW - 0.6, h: hdrH, fontFace: FF, fontSize: 12.5, bold: true, color: WHITE, valign: "middle", margin: 0 });
  s.addText("卡片正文：用 addShape 矩形拼卡片，不用 addTable。", { x: cardX + 0.16, y: cardY + hdrH + 0.1, w: cardW - 0.32, h: cardH - hdrH - 0.2, fontFace: FF, fontSize: 9.5, color: G66, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });

  // (b) tile with a GRADIENT (placeholder color → postprocess swaps to gradFill)
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cardX + cardW + 0.4, y: cardY, w: 0.6, h: 0.6, rectRadius: 0.12, fill: { color: PH[2] }, line: { type: "none" }, shadow: mkShadow(0.22, 9, 4) });
  s.addText("渐变 tile = 占位色 " + PH[2] + " → postprocess 塞 gradFill", { x: cardX + cardW + 1.1, y: cardY, w: 4.5, h: 0.6, fontFace: FF, fontSize: 9, color: G88, valign: "middle", margin: 0 });

  // (c) chip / pill row
  let chx = cardX, chy = cardY + cardH + 0.25;
  ["示例标签 A", "示例标签 B", "关键标签"].forEach((t, i) => {
    const key = i === 2; const w = estW(t, 10.5) + 0.22;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: chx, y: chy, w, h: 0.3, rectRadius: 0.15, fill: { color: key ? NAVY : C.paleBg }, line: key ? { type: "none" } : { color: BORDER, width: 0.75 } });
    s.addText(t, { x: chx, y: chy, w, h: 0.3, fontFace: FF, fontSize: 10, bold: true, color: key ? WHITE : NAVY, align: "center", valign: "middle", margin: 0 });
    chx += w + 0.1;
  });

  // (d) two-tone arrow = single homePlate (solid body) + gradient accent strip
  const ax = cardX, ay = chy + 0.55, aw = 5.0, ah = 0.7;
  s.addShape("homePlate", { x: ax, y: ay, w: aw, h: ah, fill: { color: C.paleBg }, line: { type: "none" }, shadow: mkShadow(0.15, 10, 5) });
  s.addShape(pres.shapes.RECTANGLE, { x: ax, y: ay + 0.03, w: PX(7), h: ah - 0.06, fill: { color: PH[4] }, line: { type: "none" } }); // gradient accent
  s.addText("单个 homePlate 形状（实色）+ 渐变 accent 条，无接缝", { x: ax + 0.2, y: ay, w: aw - 0.8, h: ah, fontFace: FF, fontSize: 10.5, bold: true, color: NAVY, valign: "middle", margin: 0 });

  // (e) base rail (solid, never gradient — large area)
  const rY = T.layout.heightIn - 0.95, rH = 0.66;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: rY, w: CW, h: rH, rectRadius: 0.13, fill: { color: NAVY }, line: { type: "none" }, shadow: mkShadow(0.22, 12, 5) });
  s.addText("底部基座：大面积一律纯色，不上渐变", { x: M, y: rY, w: CW, h: rH, fontFace: FF, fontSize: 12, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

  const out = process.argv[2] || "page.pptx";
  await pres.writeFile({ fileName: out });
  console.log("WROTE", out);
})();
