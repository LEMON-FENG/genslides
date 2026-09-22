# Workflow (detailed)

Initial design follows the phases below. For delivered PPTX local edits, skip HTML re-approval; for a rejected or changed direction return to one HTML brief and wait for approval. The SKILL.md revision routing controls this reference.

```
0 定模式🔒 → 1 取证·对口径 → 2 HTML真稿·方向拉齐🔒 → 3 pptxgenjs复刻 → 4 一键出包build.py → 5 校验·新眼睛QA🔒🔒 → 6 交付
```

## Phase 0 — 定模式 🔒
Use the request and approved direction. Ask only when the desired scope is unresolved.
- **① 基于现状优化** — keep the existing skeleton & visual language; minimal targeted edits (reword / relabel / add a footnote / swap a block). Output drops into the original page.
- **② 讨论方向后重构** — new structure. Align the direction with one HTML brief, get approval, then build; variants only when requested.

Principle: **adoptability (fits the deck, pre-aligned) > design perfection.** A beautiful page the user can't merge is a failure.

## Phase 1 — 取证 & 对口径
0. Default brand = KPMG (`config/theme.json`); first cut uses it. 💡 *Optional (non-KPMG only, on explicit request):* run the **style/brand capture** pass (`optional-passes.md` §C) to sample a different palette / new template into a separate `theme.<brand>.json`. Don't switch by default.
1. Render the reference deck → study 2–3 strong pages (`python scripts/render.py deck.pptx`).
2. Extract its real title/subtitle format (`python scripts/extract_deck_style.py`): master `titleStyle`, layout placeholder `defRPr`, theme `clrScheme` (tx1/tx2/accent1). When XML inheritance is ambiguous, sample a rendered pixel (`scripts/sample_color.js`). Reconcile to `config/theme.json`→`title`. Watch for **deck inconsistency** (placeholder pages vs. hand-built pages may differ) — that's usually *why* a "unify the titles" request exists; pick one standard and say which.
3. If the page encodes domain facts, **verify against authoritative sources before drawing** (web search / standards). List "standard vs. extended/custom" items. Fix errors before any layout work.

## Phase 2 — HTML 真稿 · 方向拉齐 🔒
1. Copy `templates/visualizer.html`. Build a **high-fidelity 1280×720 mockup** — this is the frontend-design stage (no `frontend-design` skill on this harness → apply `reference/design-principles.md`). CSS `linear-gradient`, `clip-path` (home-plate arrows), inline SVG icons, `box-shadow` are all free here. Theme via the CSS `:root` vars (mirror `theme.json`).
2. Screenshot: `python scripts/shoot.py page.html page.png`.
3. For a new or changed direction, show one revised HTML and wait for brief approval; offer multiple variants only if requested.
4. For initial or changed direction, iterate the HTML until approved. Keep it as design history; after delivery the latest user-edited PPTX takes precedence. Synchronize relevant edits before regenerating.
5. 💡 *Optional (②rebuild, open design space only):* fan the variants out across subagents — `optional-passes.md` §B. Hint it's available; don't fan out by default.

## Phase 3 — pptxgenjs 复刻
- Copy `templates/gen_template.js`. Reproduce the **approved** HTML — do not redesign in pptxgenjs.
- Parametric coordinates; compute vertical budget first (`node -e` a quick height sum) before writing the full script.
- Cards = `addShape` rectangles (not `addTable`, unless it's a real data table).
- Gradients: each gradient spot gets a **unique placeholder solid color** from `theme.gradients.placeholders`; large areas stay solid. (`reference/gradient-landing.md`)
- Icons: react-icons → sharp → PNG → `addImage`. hex colors **without `#`** for pptxgenjs (react-icons colors may keep `#`).

### Figure strategy (decide per slide)
- **Simple figures → native shapes.** Step boxes, pie sectors (`PIE` + `angleRange`), connectors (`LINE`, `"curvedConnector3"`), polylines, cards, tab headers, pills. Convert the approved inline SVG element by element with a deterministic mapping (rect / circle / line / polyline / path → the matching shape); when the converter meets syntax it does not know it must **throw**, never guess.
- **Complex figures → transparent base image + native overlay.** Only when the HTML look (gradient pipes, blurred glows) cannot be reproduced natively: render *just that figure* from the HTML with Chrome headless (`--default-background-color=00000000 --force-device-scale-factor=2`), crop the strip, place it as the bottom layer, and keep every icon, card, label and connector on top as native objects. Record the crop regions in a JSON beside the generator so overlay coordinates stay in sync.
- **Never** screenshot a whole figure block that carries text or icons, and never run a generic HTML→pptx auto-translator over the page — both give unmovable, unfixable blocks and misplaced icons, the exact defects users reject.
- **Measure, don't eyeball.** Probe the approved HTML in headless Chrome (`getBoundingClientRect` for cards, text and SVG `<text>`) and export a JSON of measured boxes; the generator reads positions from it, so text lands at the measured box rather than a guessed offset.
- **Cadence.** A new technique is landed on one page and verified by the user before the same pattern is batched; batched pages are then verified in one pass.

## Phase 4 — 一键出包 🔒 (`scripts/build.py`)
```
python scripts/build.py gen_page.js page.pptx [--theme=config/theme.<firm>.json]
```
One atomic gate, five steps, any failure exits nonzero:
1. **generate** — `node gen_page.js` with `NODE_PATH` + `GENSLIDES_THEME` set (works for generators copied into working folders).
2. **postprocess** — font slots (latin/cs→`theme.fonts.latin`, keep ea), move `notesMasterIdLst` before `sldIdLst`, strip stray zip directory entries, swap gradient placeholders→`<a:gradFill>`.
3. **house checks** — bundled `check_pptx.py`: PowerPoint "needs-repair" causes + leftover `EE00xx` placeholders + `#` in hex + gold warning.
4. **validate** — the configured `validate.py` (stronger XSD) if `config/env.json` points at one.
5. **render** — LibreOffice→JPG; paths printed for eyeballing and the QA pass.

Generator changes require GATE PASS. Direct existing-PPTX edits use equivalent package checks and rendered-page QA; never regenerate from stale source to satisfy a label.

## Phase 5 — 校验 · 新眼睛 QA 🔒🔒
1. 🔒 Generator output passed Phase 4; direct PPTX edits passed equivalent package checks and rendered-page QA.
2. On the rendered JPG, run a **fresh-eyes QA** pass (the gate — objective defect hunt): in Claude Code spawn the **`slide-qa`** subagent (image path + intended-content paragraph); fallback ladder in `qa-prompt.md`. List actual issues, fix them, then repeat the applicable generation or direct-PPTX validation path until a clean pass. One fix often creates another.
3. Walk `reference/self-check.md`.
4. 💡 *Optional (only if clean-but-flat):* offer the 3-dim polish-grade review via **`slide-critic`** — `optional-passes.md` §A. Ceiling-raiser, **not a gate**; hint it's available, don't run by default.

## Phase 6 — 交付
- For new sample pages deliver a standalone `.pptx`; for requested deck edits deliver a new version based on the latest deck. Standalone pages can be merged by the user (the deck's master applies footers/page numbers — that's why this skill draws **no footer**).
- Replacing pages inside the user's deck (only when authorized): re-read the deck from disk first (users hand-edit in PowerPoint between rounds), back up the hand-edited version, and never write while a `~$` lock file exists. Match pages by title, keep the original position and hidden flag, and carry renamed titles through an explicit title map. With python-pptx: add all new slides → move them → delete the old slides last and `drop_rel` them; when copying a slide between decks, re-attach image relationships (`get_or_add_image_part` + rewrite `a:blip r:embed`).
