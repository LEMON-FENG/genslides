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
| pie / sector | `pres.shapes.PIE` + `angleRange:[a0,a1]` in degrees; 0 = 3 o'clock, clockwise |
| `CURVED_CONNECTOR_3` | not in the `shapes` enum → pass the raw preset name `"curvedConnector3"` to `addShape` (it only checks non-empty); orient with `flipH: x2<x1, flipV: y2<y1` |
| `LINE` direction | a LINE is drawn top-left → bottom-right of its bbox; a bottom-left → top-right segment needs `flipV:true` |
| filled polygon | only `CUSTOM_GEOMETRY` takes a fill; a chain of `LINE`s stays hollow |
| `rotate` outside 0–360 | `convertRotationDegrees` rejects it → normalize the angle first |

## Figures (HTML → slide)
- Whole-block screenshots of a figure and generic HTML→pptx auto-translators both fail the same way: unmovable image blocks, misplaced icons, text the user cannot edit. Simple figures are native shapes; only an irreproducible complex figure is a transparent base image with native icons/cards/text on top. See `workflow.md` → Phase 3 → Figure strategy.
- Before reporting a "defect" in a delivered page, check the file's coordinates and the page's history: an icon that looks off in a screenshot may have been dragged by the user, and an older page may be a standard-flow original rather than a regression.

## Deck assembly (python-pptx)
- Replace pages by title, keep position and hidden flag; three-phase order (add all → move → delete old + `drop_rel`) avoids dangling relationships.
- Copying a slide across decks: `deepcopy` of the shape tree is not enough — every `a:blip r:embed` must be re-pointed at an image part added to the target slide (`get_or_add_image_part`).
- Users hand-edit in PowerPoint between rounds: re-read from disk, back up the hand-edited file, never write while `~$<name>.pptx` exists.

## Layout
- **Compute the vertical budget first.** The most common defect is a block that needs more height than it has → everything overlaps. `node -e` a quick sum before writing the full script.
- Parametric anchors: derive every y from a few variables (`cardY → connY → titleY → bodyY`) so one change cascades.
- Big number table: keep one **right rail** per column; align headline/subtotal values to the rightmost column's rail; put a `—` for empty cells on the same rail.
- Sign chips: a fixed chip column + absolute-magnitude values. Never `－` chip next to a `-123` number (double sign reads as a typo).

## LibreOffice render ≠ PowerPoint
- XML validation and LibreOffice previews do not prove PowerPoint compatibility. Use the native temporary-copy check when available; otherwise state **PowerPoint NOT VERIFIED**. See [PowerPoint compatibility](powerpoint-compatibility.md) for PNG normalization, native checks, and their limits.
- Super-wide super-short text boxes with tiny fonts, or edge shapes with large blur shadows, can crash the LibreOffice importer (`STACK_BUFFER_OVERRUN`) without harming the actual PowerPoint file — bisect with a head-cut script to locate.

## 🔴 OOXML validation (gate before delivery)
`python scripts/build.py gen_page.js page.pptx` chains generate→postprocess→house checks→validate→render and must end **GATE PASS** — use it instead of hand-running steps. Known breakers the chain catches:
1. **`notesMasterIdLst` ordering** — pptxgenjs emits it after `sldIdLst`; schema requires it before. `postprocess.py` moves it after `</p:sldMasterIdLst>`.
   **Shared notes theme:** before delivering reordered output, keep notes-master themes independent from slide-master themes. Native tests reproduced a loader failure after reordering when both referenced the same theme; `theme_compatibility.py` clones the theme and optional theme relationships without deleting notes content.
2. **Gradient post-process** — easy to malform; validate right after.
3. **Font slots** — pptxgenjs fills latin/ea/cs identically; `postprocess.py` sets latin/cs→latin font, keeps ea.
4. **Leftover `EE00xx` placeholder / `#` in hex** — `check_pptx.py` house checks fail on both; gold `EAAA00` warns.
Order: **validate first (it opens?) → then LibreOffice render (layout)** — build.py already enforces this.

**Validate step flakes on the network.** The external `validate.py` downloads the Dublin Core XSD; a network hiccup shows up as `4 validate [FAIL]` while generate / postprocess / house checks passed. That is not a broken file: rerun `validate.py` on the produced `.pptx` alone (retry a few times), then run `scripts/powerpoint_check.py` on it. Never skip the check or declare the file bad on that evidence alone.

**Harness note (Windows Git Bash).** A bash heredoc that writes a generator containing CJK text or JavaScript quotes can die with `unexpected EOF while looking for matching quote`. Write generator files with the editor/Write tool or a Python script, not via a bash heredoc.

### ⚠️ "PowerPoint needs to repair" though everything validates
pptxgenjs **4.0.x** injects **stray empty directory entries** into the .pptx zip (e.g. `_rels/`, `ppt/_rels/`, and an orphan `ppt/charts/_rels/` even with no charts). OPC packages must contain only *part* (file) entries. **PowerPoint's strict package loader rejects folder entries → "needs repair"**, while LibreOffice, python-pptx, and validate.py (XSD) all **ignore them and pass** — so the gates won't catch it. `postprocess.py` strips every entry whose name ends in `/`. Verify with: a clean package has **zero** entries ending in `/`. (This affects *any* pptxgenjs 4.0.x output, not just genslides.)
