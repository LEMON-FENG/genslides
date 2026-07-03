# Workflow (detailed)

The 6-phase loop. The 4 🔒 gates are non-negotiable.

```
0 定模式🔒 → 1 取证·对口径 → 2 HTML真稿·方向拉齐🔒 → 3 pptxgenjs复刻 → 4 一键出包build.py → 5 校验·新眼睛QA🔒🔒 → 6 交付
```

## Phase 0 — 定模式 🔒
Ask, never assume (in Claude Code use **AskUserQuestion**; skip only if the invocation arguments already carried ①/②):
- **① 基于现状优化** — keep the existing skeleton & visual language; minimal targeted edits (reword / relabel / add a footnote / swap a block). Output drops into the original page.
- **② 讨论方向后重构** — new structure. Align the *direction* first (Phase 2 gives variants), get a nod, then build.

Principle: **adoptability (fits the deck, pre-aligned) > design perfection.** A beautiful page the user can't merge is a failure.

## Phase 1 — 取证 & 对口径
0. Default brand = KPMG (`config/theme.json`); first cut uses it. 💡 *Optional (non-KPMG only, on explicit request):* run the **style/brand capture** pass (`optional-passes.md` §C) to sample a different palette / new template into a separate `theme.<brand>.json`. Don't switch by default.
1. Render the reference deck → study 2–3 strong pages (`python scripts/render.py deck.pptx`).
2. Extract its real title/subtitle format (`python scripts/extract_deck_style.py`): master `titleStyle`, layout placeholder `defRPr`, theme `clrScheme` (tx1/tx2/accent1). When XML inheritance is ambiguous, sample a rendered pixel (`scripts/sample_color.js`). Reconcile to `config/theme.json`→`title`. Watch for **deck inconsistency** (placeholder pages vs. hand-built pages may differ) — that's usually *why* a "unify the titles" request exists; pick one standard and say which.
3. If the page encodes domain facts, **verify against authoritative sources before drawing** (web search / standards). List "standard vs. extended/custom" items. Fix errors before any layout work.

## Phase 2 — HTML 真稿 · 方向拉齐 🔒
1. Copy `templates/visualizer.html`. Build a **high-fidelity 1280×720 mockup** — this is the frontend-design stage (no `frontend-design` skill on this harness → apply `reference/design-principles.md`). CSS `linear-gradient`, `clip-path` (home-plate arrows), inline SVG icons, `box-shadow` are all free here. Theme via the CSS `:root` vars (mirror `theme.json`).
2. Screenshot: `python scripts/shoot.py page.html page.png`.
3. **②rebuild → give 2–3 direction variants** (`page_甲.html / _乙.html / _丙.html`), let the user choose before building anything (AskUserQuestion in Claude Code).
4. Iterate on HTML (fast) until signed off. Keep `*.html` + screenshot beside the generator as the page's source of truth.
5. 💡 *Optional (②rebuild, open design space only):* fan the variants out across subagents — `optional-passes.md` §B. Hint it's available; don't fan out by default.

## Phase 3 — pptxgenjs 复刻
- Copy `templates/gen_template.js`. Reproduce the **approved** HTML — do not redesign in pptxgenjs.
- Parametric coordinates; compute vertical budget first (`node -e` a quick height sum) before writing the full script.
- Cards = `addShape` rectangles (not `addTable`, unless it's a real data table).
- Gradients: each gradient spot gets a **unique placeholder solid color** from `theme.gradients.placeholders`; large areas stay solid. (`reference/gradient-landing.md`)
- Icons: react-icons → sharp → PNG → `addImage`. hex colors **without `#`** for pptxgenjs (react-icons colors may keep `#`).

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

Must end **GATE PASS**. Rerun after *any* change to the generator or theme — never deliver a page whose last build didn't pass.

## Phase 5 — 校验 · 新眼睛 QA 🔒🔒
1. 🔒 Phase 4 printed **GATE PASS** (this subsumes the old "validate.py must PASS" rule).
2. On the rendered JPG, run a **fresh-eyes QA** pass (the gate — objective defect hunt): in Claude Code spawn the **`slide-qa`** subagent (image path + intended-content paragraph); fallback ladder in `qa-prompt.md`. List issues → fix → rerun `build.py` → repeat until a full clean pass. One fix often creates another.
3. Walk `reference/self-check.md`.
4. 💡 *Optional (only if clean-but-flat):* offer the 3-dim polish-grade review via **`slide-critic`** — `optional-passes.md` §A. Ceiling-raiser, **not a gate**; hint it's available, don't run by default.

## Phase 6 — 交付
- Standalone `.pptx` to the working folder. The user merges it into the master deck by hand (the deck's master applies footers/page numbers — that's why this skill draws **no footer**).
