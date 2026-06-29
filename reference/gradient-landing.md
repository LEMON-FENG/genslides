# Gradient landing: HTML CSS gradient → editable pptx gradFill

pptxgenjs has **no gradient API**. The house technique keeps gradients as *editable surface fills* (selectable, recolorable, movable in PowerPoint) — never baked images, never the slide background.

## The five rules
1. **In HTML, gradients are free** — use `linear-gradient` for card top-bars, tiles, accent strips, badges, two-tone arrow tips.
2. **In gen.js, every gradient spot gets a UNIQUE placeholder solid color** (`EE0001…EE00xx`), defined once: `const PH = { TILE: "EE0003", BADGE: "EE0008", ... }`.
3. **Large areas stay SOLID** — arrow bodies (`homePlate`), base rails, big bands. Only small accents/tiles/badges/top-bars get gradients. Big gradients look heavy and break more easily.
4. **After `node` generates the pptx, `postprocess.py` swaps each placeholder** `<a:solidFill><a:srgbClr val="EE00xx"/></a:solidFill>` → `<a:gradFill> … <a:lin ang="…"/></a:gradFill>` using `theme.json → gradients.placeholders[EE00xx]` (stops + angle).
5. 🔒 **Re-run `validate.py` after the swap.** Gradient post-processing is the easiest way to break OOXML (PowerPoint is stricter than LibreOffice/markitdown — markitdown parsing ≠ PowerPoint opening).

## Angle map (`theme.gradients.angles`)
| name | `ang` value | direction |
|------|-------------|-----------|
| horizontal | 0 | left→right |
| vertical | 5400000 | top→bottom |
| diag45 | 2700000 | ↗ 45° |
| diag135 | 8100000 | ↘ 135° |

## Adding a new gradient
1. In the HTML, style it with `linear-gradient` and eyeball the two stops + direction.
2. In gen.js, fill that shape with a new placeholder color `EE00xx` (must be unique on the slide).
3. Add `"EE00xx": { "stops": ["<from>", "<to>"], "angle": "<name>" }` to `theme.json → gradients.placeholders`.
4. Generate → `postprocess.py` → `validate.py` → render and eyeball.

## Two-tone arrows
HTML uses `clip-path: polygon(...)` for a home-plate body + a `tip` triangle. In pptx, prefer a **single `homePlate` shape** (one shape, one shadow → no seam). If you need a genuine two-tone, use a rectangle body + a 90°-rotated `ISOSCELES_TRIANGLE` head (standard shapes, consistent across LibreOffice/PowerPoint). Never rely on `homePlate`/`PENTAGON` adjustment depth matching a separate rectangle — they diverge between renderers.

## Solid-first fallback
If a gradient isn't essential, ship it solid. Gradients are polish; correctness and "opens in PowerPoint" come first.
