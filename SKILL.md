---
name: genslides
description: Produce a single high-quality, on-brand presentation slide (.pptx) using an HTML-mockup-first → pptxgenjs → validate workflow. Ships with four built-in Big-Four consulting styles (KPMG by default, plus Deloitte / PwC / EY), switchable in config/theme.json and configurable to any brand. Use when asked to design, beautify, or rebuild a deck page for consulting / bid / executive decks. Composes the `pptx` and `frontend-design` skills and enforces four gates: mode-alignment, HTML direction sign-off, OOXML validation, and fresh-eyes QA. Keep end-client names out of the skill.
---

# genslides

A reusable workflow for crafting **one polished slide at a time**, then delivering it as a standalone `.pptx` the user merges into their master deck by hand. Ships with **four built-in Big-Four consulting styles** — **KPMG** (default) · **Deloitte** · **PwC** · **EY** — switchable via `config/theme.json` (set env `GENSLIDES_THEME=config/theme.<firm>.json`), and configurable to any brand.

The defining idea: **decide the visuals on a fast HTML mockup first, sign it off, then faithfully reproduce that mockup in pptxgenjs** — never design straight in pptxgenjs. Gradients and brand colors live as *editable* fills, not baked images.

> This skill is a **living template**. `config/theme.json` is the single source of truth for the brand (default KPMG) — palette / fonts / title spec — edit it to re-skin everything. `templates/` and `scripts/` are meant to be copied and improved per engagement. Keep **end-client** names out (乐美/商米/etc.); put engagement-specific facts in the working folder, not here. The firm brand (KPMG) is the default and is fine to name.

## When to use
- "美化/重做/设计 这一页 slide"、"做一页咨询/述标风格的 pptx 样品页"、"把这张表做漂亮"
- Any request to produce or restyle a single deck page as a deliverable `.pptx`.
- Not for: editing an existing multi-slide deck in place (use `pptx`), or bulk text extraction (use `pptx` → markitdown).

## Composes two skills
- **frontend-design** — drives the HTML mockup stage: distinctive, non-generic visual design (palette layering, whitespace, a repeated motif, typography). Invoke its guidance when building `templates/visualizer.html`.
- **pptx** — drives generation + QA: pptxgenjs reference, `soffice`→pdf→image rendering, markitdown extraction, `validate.py`, and the fresh-eyes QA methodology.

genslides is the **orchestrator** that wires them together and adds the house layer (theme, env paths, gradient-landing post-process, and the gates).

## Workflow (6 phases, 4 gates 🔒)

```
0 定模式🔒 → 1 取证·对口径 → 2 HTML 真稿·方向拉齐🔒 → 3 pptxgenjs 复刻
                                                          → 4 后处理 → 5 校验·新眼睛QA🔒🔒 → 6 交付
```

**Phase 0 — 定模式 🔒 (ask, never assume)**
Before touching anything, ask the user: is this page **① optimize-current** (keep the skeleton, minimal targeted edits, drop-in) or **② rebuild-after-aligning-direction**? For ②, you must align the *direction* first (Phase 2 gives 2–3 variants). Rule: **adoptability (fits the deck, pre-aligned) > design perfection.**

**Phase 1 — 取证 & 对口径**
- Default brand = KPMG (`config/theme.json`). Build the first cut on it. 💡 *Optional (non-KPMG only):* if the user wants a different palette/brand or to match a brand-new template, offer the **style/brand capture** pass — `reference/optional-passes.md` §C — which samples colors + title format into a *separate* `theme.<brand>.json` (KPMG default untouched). Hint it's available; don't switch brands by default.
- Render the reference deck (see `scripts/render.ps1`); study 2–3 strong pages for the visual language.
- Extract the deck's real title/subtitle format with `scripts/extract_deck_style.js`; sample a rendered pixel with `scripts/sample_color.js` when XML inheritance is ambiguous. Reconcile against `config/theme.json` → `title`.
- If the page encodes domain facts (finance/accounting/data logic), **verify against authoritative sources before drawing** and list "standard vs. extended" items. Fix errors first.

**Phase 2 — HTML 真稿 · 方向拉齐 🔒**
- Build a high-fidelity HTML mockup from `templates/visualizer.html` (1280×720, themed via CSS vars from `theme.json`). This is where **frontend-design** quality happens — CSS gradients, `clip-path`, inline SVG icons, shadows are all free here.
- Screenshot with `scripts/shoot.ps1` (Chrome headless). For **②rebuild**, produce 2–3 *direction variants* (e.g. `*_甲.html / *_乙.html / *_丙.html`) and have the user pick before proceeding.
- Iterate on HTML until signed off. Keep `*.html` + screenshot as the page's source of truth.
- 💡 *Optional (②rebuild, open design space):* you may fan out parallel direction variants via subagents — see `reference/optional-passes.md` §B. Mention it's available; don't fan out by default.

**Phase 3 — pptxgenjs 复刻**
- Copy `templates/gen_template.js`; reproduce the **approved** HTML faithfully. Parametric coordinates, compute heights first. See `reference/house-style.md` and `reference/pitfalls.md`.
- Small accents/tiles/badges/top-bars that need gradients get a **unique placeholder solid color**; large areas stay solid. See `reference/gradient-landing.md`.

**Phase 4 — 后处理** (`scripts/postprocess.py`)
- Font slots: latin/cs → `theme.fonts.latin`, ea → `theme.fonts.eastasian`.
- Fix pptxgenjs `notesMasterIdLst` ordering bug.
- Replace gradient placeholder colors with `<a:gradFill>` (config-driven from `theme.gradients`).

**Phase 5 — 校验 · 自查 🔒🔒**
- 🔒 the validator must print **"All validations PASSED!"** — bundled `scripts/check_pptx.py` (self-contained, catches the PowerPoint "needs-repair" causes), or the `pptx` skill's `validate.py` if installed (stronger XSD). Run again after any gradient post-process.
- Render to image; then run a **fresh-eyes QA subagent** with `reference/qa-prompt.md` (this is the gate — objective defect hunt). Fix → re-render → repeat until a clean pass. Walk `reference/self-check.md`.
- 💡 *Optional (only if the page is clean-but-flat):* offer a 3-dim **polish-grade review** (视觉层级 / 品牌口径一致性 / 细节执行) — see `reference/optional-passes.md` §A. It's a ceiling-raiser, **not a gate**; mention it's available, don't run by default.

**Phase 6 — 交付**
- Deliver a **standalone `.pptx`** to the working folder. Never touch a deck the user is editing by hand.

## Verify the skill works
Run the self-test (exercises the whole chain on this machine):
```
pwsh -NoProfile -File scripts/selftest.ps1
```
Expect `RESULT: ALL PASS ✓` across 5 steps (generate → postprocess → validate.py gate → LibreOffice render → Chrome shoot), plus two image paths to eyeball. Any FAIL points at a wrong path in `config/env.json`.
Per-page verification is the gates themselves: every delivered page must show **"All validations PASSED!"**, a render image, and a clean fresh-eyes QA report.

## Files
- `config/theme.json` — 🎨 palette, fonts, title spec, gradient map, layout. **Edit this to re-skin.**
- `config/env.json` — tool paths (node modules, soffice, chrome, pdftoppm, validate/unpack). Edit per machine.
- `reference/` — `workflow.md`, `house-style.md`, `title-spec.md`, `gradient-landing.md`, `pitfalls.md`, `self-check.md`, `qa-prompt.md`, `optional-passes.md` (opt-in extras: polish-grade review + parallel variants — hint-only, not gates).
- `templates/` — `visualizer.html` (HTML mockup skeleton), `gen_template.js` (pptxgenjs house template).
- `scripts/` — `setup.ps1`, `selftest.ps1`, `shoot.ps1` (HTML→PNG), `render.ps1` (pptx→images), `postprocess.py`, `check_pptx.py` (bundled MIT validator — the gate), `sample_color.js`, `extract_deck_style.py`, `capture_palette.js` (opt-in brand capture).

## Hard rules (red lines)
- Never automate PowerPoint (no COM); only ever write new/standalone files.
- Never assume the edit mode — ask ①/② first.
- No gold; no footer summary bar.
- Gradients/atmosphere must be **editable surface fills** (placeholder→gradFill), never baked into images or the slide background.
- Business-formal copy, no AI-isms / slogans; keep standard domain terms, never invent examples.
- Always pass `validate.py` and a fresh-eyes QA pass before declaring done.
