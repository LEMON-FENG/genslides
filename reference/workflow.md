# Workflow (detailed)

The 6-phase loop. The 4 🔒 gates are non-negotiable.

```
0 定模式🔒 → 1 取证·对口径 → 2 HTML真稿·方向拉齐🔒 → 3 pptxgenjs复刻 → 4 后处理 → 5 校验·新眼睛QA🔒🔒 → 6 交付
```

## Phase 0 — 定模式 🔒
Ask, never assume:
- **① 基于现状优化** — keep the existing skeleton & visual language; minimal targeted edits (reword / relabel / add a footnote / swap a block). Output drops into the original page.
- **② 讨论方向后重构** — new structure. Align the *direction* first (Phase 2 gives variants), get a nod, then build.

Principle: **adoptability (fits the deck, pre-aligned) > design perfection.** A beautiful page the user can't merge is a failure.

## Phase 1 — 取证 & 对口径
0. Default brand = KPMG (`config/theme.json`); first cut uses it. 💡 *Optional (non-KPMG only, on explicit request):* run the **style/brand capture** pass (`optional-passes.md` §C) to sample a different palette / new template into a separate `theme.<brand>.json`. Don't switch by default.
1. Render the reference deck → study 2–3 strong pages (`scripts/render.ps1`).
2. Extract its real title/subtitle format (`scripts/extract_deck_style.py`): master `titleStyle`, layout placeholder `defRPr`, theme `clrScheme` (tx1/tx2/accent1). When XML inheritance is ambiguous, sample a rendered pixel (`scripts/sample_color.js`). Reconcile to `config/theme.json`→`title`. Watch for **deck inconsistency** (placeholder pages vs. hand-built pages may differ) — that's usually *why* a "unify the titles" request exists; pick one standard and say which.
3. If the page encodes domain facts, **verify against authoritative sources before drawing** (web search / standards). List "standard vs. extended/custom" items. Fix errors before any layout work.

## Phase 2 — HTML 真稿 · 方向拉齐 🔒
1. Copy `templates/visualizer.html`. Build a **high-fidelity 1280×720 mockup** — this is the frontend-design stage. CSS `linear-gradient`, `clip-path` (home-plate arrows), inline SVG icons, `box-shadow` are all free here. Theme via the CSS `:root` vars (mirror `theme.json`).
2. Screenshot: `scripts/shoot.ps1 page.html page.png`.
3. **②rebuild → give 2–3 direction variants** (`page_甲.html / _乙.html / _丙.html`), let the user choose before building anything.
4. Iterate on HTML (fast) until signed off. Keep `*.html` + screenshot beside the generator as the page's source of truth.
5. 💡 *Optional (②rebuild, open design space only):* fan the variants out across subagents — `optional-passes.md` §B. Hint it's available; don't fan out by default.

## Phase 3 — pptxgenjs 复刻
- Copy `templates/gen_template.js`. Reproduce the **approved** HTML — do not redesign in pptxgenjs.
- Parametric coordinates; compute vertical budget first (`node -e` a quick height sum) before writing the full script.
- Cards = `addShape` rectangles (not `addTable`, unless it's a real data table).
- Gradients: each gradient spot gets a **unique placeholder solid color** from `theme.gradients.placeholders`; large areas stay solid. (`reference/gradient-landing.md`)
- Icons: react-icons → sharp → PNG → `addImage`. hex colors **without `#`** for pptxgenjs (react-icons colors may keep `#`).

## Phase 4 — 后处理 (`scripts/postprocess.py file.pptx`)
1. Font slots: latin/cs → `theme.fonts.latin`, ea → `theme.fonts.eastasian`.
2. Move `notesMasterIdLst` before `sldIdLst` (pptxgenjs ordering bug → PowerPoint "needs repair").
3. Replace gradient placeholder colors with `<a:gradFill>` per `theme.gradients`.

## Phase 5 — 校验 · 自查 🔒🔒
1. 🔒 `validate.py file.pptx` → must print **"All validations PASSED!"**. Re-run after any gradient post-process (it's the easiest way to break OOXML).
2. Render to image (`scripts/render.ps1`), then run a **fresh-eyes QA subagent** with `reference/qa-prompt.md` (the gate — objective defect hunt). List issues → fix → re-render → repeat until a full clean pass. One fix often creates another.
3. Walk `reference/self-check.md`.
4. 💡 *Optional (only if clean-but-flat):* offer the 3-dim polish-grade review — `optional-passes.md` §A. Ceiling-raiser, **not a gate**; hint it's available, don't run by default.

## Phase 6 — 交付
- Standalone `.pptx` to the working folder. The user merges it into the master deck by hand (the deck's master applies footers/page numbers — that's why this skill draws **no footer**).
