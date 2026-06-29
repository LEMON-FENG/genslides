# Pitfalls (pptxgenjs / LibreOffice ≠ PowerPoint / OOXML)

## pptxgenjs API
| pitfall | fix |
|---|---|
| hex color with `#` | write `"00338D"`, **never** `#`. (react-icons colors *may* keep `#`.) |
| 8-digit hex for alpha | use the `transparency`/`opacity` option, never bake alpha into the color string |
| shared option object | pptxgenjs mutates option objects in place → use a **factory** `mkShadow()` that returns a fresh object each call |
| `TRIANGLE` shape | doesn't exist → `pres.shapes.ISOSCELES_TRIANGLE`; right-pointing = `+ rotate:90` (position by pre-rotation bbox center) |
| unicode bullet `•` | use `bullet:true`, not a literal `•` |
| multi-line rich text | add `breakLine:true` between runs |
| reusing a pres instance | `new pptxgen()` per file |
| rounded-rect + a covering rectangle strip | corners leak → use a plain `RECTANGLE` when you need a covering strip, or inset the strip |
| `rectRadius` too large | it's an absolute-inch value; a "pill" with `rad:0.5` can exceed half-height → illegal geometry → LibreOffice crash. Clamp `rad = min(rad, min(W,H)/2)` |

## Layout
- **Compute the vertical budget first.** The most common defect is a block that needs more height than it has → everything overlaps. `node -e` a quick sum before writing the full script.
- Parametric anchors: derive every y from a few variables (`cardY → connY → titleY → bodyY`) so one change cascades.
- Big number table: keep one **right rail** per column; align headline/subtotal values to the rightmost column's rail; put a `—` for empty cells on the same rail.
- Sign chips: a fixed chip column + absolute-magnitude values. Never `－` chip next to a `-123` number (double sign reads as a typo).

## LibreOffice render ≠ PowerPoint
- LibreOffice only proves "shapes don't detach / don't overflow". **Final check must be a real PowerPoint render** (or at least trust validate.py + careful visual QA).
- Super-wide super-short text boxes with tiny fonts, or edge shapes with large blur shadows, can crash the LibreOffice importer (`STACK_BUFFER_OVERRUN`) without harming the actual PowerPoint file — bisect with a head-cut script to locate.

## 🔴 OOXML validation (gate before delivery)
Run `python <validatePy> file.pptx` → must see **"All validations PASSED!"**. Known breakers:
1. **`notesMasterIdLst` ordering** — pptxgenjs emits it after `sldIdLst`; schema requires it before. `postprocess.py` moves it after `</p:sldMasterIdLst>`.
2. **Gradient post-process** — easy to malform; validate right after.
3. **Font slots** — pptxgenjs fills latin/ea/cs identically; `postprocess.py` sets latin/cs→latin font, keeps ea.
Order: **validate.py first (it opens?) → then LibreOffice render (layout)**.

### ⚠️ "PowerPoint needs to repair" though everything validates
pptxgenjs **4.0.x** injects **stray empty directory entries** into the .pptx zip (e.g. `_rels/`, `ppt/_rels/`, and an orphan `ppt/charts/_rels/` even with no charts). OPC packages must contain only *part* (file) entries. **PowerPoint's strict package loader rejects folder entries → "needs repair"**, while LibreOffice, python-pptx, and validate.py (XSD) all **ignore them and pass** — so the gates won't catch it. `postprocess.py` strips every entry whose name ends in `/`. Verify with: a clean package has **zero** entries ending in `/`. (This affects *any* pptxgenjs 4.0.x output, not just genslides.)
