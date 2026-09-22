---
name: genslides
description: "Design or revise an on-brand PPTX page. First or changed directions use one HTML brief before PPTX; local revisions directly edit the latest delivered PPTX with QA. Return to HTML when the user rejects the direction."
argument-hint: "[①优化|②重构] [--theme=kpmg|deloitte|pwc|ey]"
allowed-tools: Bash(node:*), Bash(python:*), Bash(pwsh:*)
---

# genslides

A reusable workflow for crafting **one polished slide at a time**, then delivering it as a standalone `.pptx` the user merges into their master deck by hand. Ships with **four built-in Big-Four consulting styles** — **KPMG** (default) · **Deloitte** · **PwC** · **EY** — switchable via `config/theme.json`, and configurable to any brand.

The defining idea: **decide the visuals on a fast HTML mockup first, sign it off, then faithfully reproduce that mockup in pptxgenjs** — use the approved direction for initial generation; later local edits follow the latest PPTX. Gradients and brand colors live as *editable* fills, not baked images.

> This skill is a **living template**. `config/theme.json` is the single source of truth for the brand (default KPMG) — palette / fonts / title spec — edit it to re-skin everything. `templates/` and `scripts/` are meant to be copied and improved per engagement. Keep **end-client** names out (乐美/商米/etc.); put engagement-specific facts in the working folder, not here. The firm brand (KPMG) is the default and is fine to name.

## Arguments

Invocation may carry arguments: `$ARGUMENTS`

- `①` / `②` (or `优化` / `重构`) — pre-answers the Phase-0 mode question; skip the ask.
- `--theme=<firm>` — use `config/theme.<firm>.json` (deloitte / pwc / ey); pass it through as `scripts/build.py --theme=...`. Default is KPMG (`config/theme.json`).
- No arguments: use the user's natural-language request and already approved direction; ask only when optimize versus redesign is materially unclear.

## When to use
- "美化/重做/设计 这一页 slide"、"做一页咨询/述标风格的 pptx 样品页"、"把这张表做漂亮"
- Any request to produce or restyle a single deck page as a deliverable `.pptx`.
- Not for: editing an existing multi-slide deck in place (use `pptx`), or bulk text extraction (use `pptx` → markitdown).

## Composes two skills
- **frontend-design** — drives the HTML mockup stage: distinctive, non-generic visual design (palette layering, whitespace, a repeated motif, typography). Invoke its guidance when building `templates/visualizer.html`. *Harness without that skill:* use the bundled distillation `reference/design-principles.md` instead — never skip the design pass.
- **pptx** — drives generation + QA: pptxgenjs reference, `soffice`→pdf→image rendering, markitdown extraction, `validate.py`, and the fresh-eyes QA methodology. *Harness without that skill:* the bundled `scripts/check_pptx.py` covers validation; rendering is `scripts/render.py`.

genslides is the **orchestrator** that wires them together and adds the house layer (theme, env paths, gradient-landing post-process, and the gates).

## Workflow (6 phases, 4 gates 🔒)

```
0 定模式🔒 → 1 取证·对口径 → 2 HTML 真稿·方向拉齐🔒 → 3 pptxgenjs 复刻
                                             → 4 一键出包 build.py → 5 校验·新眼睛QA🔒🔒 → 6 交付
```

**Phase 0 — Determine whether the direction changed**
Use arguments, natural language and prior approval together. Small edits to an existing approved PPTX (text, size, spacing, local elements) go directly to the latest deck or synchronized generator without a new HTML approval. If the user says the drawing/expression is wrong, asks for another direction, or requests a new HTML brief, return to Phase 2, show one revised HTML, obtain brief approval, then build PPTX. Produce variants only when the user asks to compare directions. Ask about mode only if genuinely unresolved.
分轮提问：若除模式外还有影响方向的未决点（页面主题、内容范围、母版/主题色），与模式问题**合并成一轮**问完，每题编号并附推荐选项+一句理由；不分散多次追问。

**Phase 1 — 取证 & 对口径**
- Default brand = KPMG (`config/theme.json`). Build the first cut on it. 💡 *Optional (non-KPMG only):* if the user wants a different palette/brand or to match a brand-new template, offer the **style/brand capture** pass — `reference/optional-passes.md` §C — which samples colors + title format into a *separate* `theme.<brand>.json` (KPMG default untouched). Hint it's available; don't switch brands by default.
- Render the reference deck (`python scripts/render.py deck.pptx`); study 2–3 strong pages for the visual language.
- Extract the deck's real title/subtitle format with `scripts/extract_deck_style.py`; sample a rendered pixel with `scripts/sample_color.js` when XML inheritance is ambiguous. Reconcile against `config/theme.json` → `title`.
- If the page encodes domain facts (finance/accounting/data logic), **verify against authoritative sources before drawing** and list "standard vs. extended" items. Fix errors first.

**Phase 2 — HTML 真稿 · 方向拉齐 🔒**
- Build a high-fidelity HTML mockup from `templates/visualizer.html` (1280×720, themed via CSS vars from `theme.json`). This is where **frontend-design** quality happens (fallback: `reference/design-principles.md`) — CSS gradients, `clip-path`, inline SVG icons, shadows are all free here.
- Screenshot the HTML. For a first design or changed direction show one focused draft and wait for the user's brief approval before PPTX. Multiple variants are optional only when requested.
- Brief 确认后的局部修正直接完成；用户否定表达或要求换方向时，重出一稿 HTML 再 brief 确认。新发现关键事实或权限问题只暂停相关部分。
- HTML approval is for a new or changed direction. Minor revisions after PPTX delivery do not return to HTML. The latest user-edited PPTX takes precedence over stale HTML/generator; synchronize relevant changes before any regeneration.
- 💡 *Optional (②rebuild, open design space):* you may fan out parallel direction variants via subagents — see `reference/optional-passes.md` §B. Mention it's available; don't fan out by default.

**Phase 3 — pptxgenjs 复刻**
- Copy `templates/gen_template.js`; reproduce the **approved** HTML faithfully. Parametric coordinates, compute heights first. See `reference/house-style.md` and `reference/pitfalls.md`.
- Small accents/tiles/badges/top-bars that need gradients get a **unique placeholder solid color**; large areas stay solid. See `reference/gradient-landing.md`.
- **Figures: decide per slide, never per deck.** Simple diagrams (step boxes, pie sectors, connectors, cards, tab headers) are rebuilt as **native pptxgenjs shapes** so the user can edit every item. Only a complex figure whose HTML look cannot be reproduced natively (e.g. gradient pipes) becomes an image — and then only that figure, rendered from the HTML as a **transparent PNG base layer**, with its icons, cards and text still native on top. Never screenshot a whole figure block that contains text or icons; never run a generic HTML→pptx auto-translator over the page. Details: `reference/workflow.md` → Phase 3 → Figure strategy.
- **New technique → one page first.** Land one page, let the user verify it, then batch the pages that share the pattern and let the user verify those in one pass.

**Phase 4 — 一键出包 🔒 (`scripts/build.py`)**
```
python scripts/build.py gen_page.js page.pptx [--theme=config/theme.<firm>.json]
```
For generator-based creation, one atomic command: generate → postprocess → checks → render; it must end with GATE PASS. For targeted edits to an existing PPTX use its native editing/validation path, render affected pages and inspect them; do not rerun a stale generator merely to obtain that label.

The build isolates shared notes-master themes and normalizes embedded static PNGs losslessly before validation, then uses PowerPoint on temporary copies when Windows COM is available. `--powerpoint=required` requires that native check; `auto` is the default. Native failure stops the build; do not bypass it with LibreOffice. Without PowerPoint, alternate-render output is explicitly **PowerPoint NOT VERIFIED**. `--no-render` is a static diagnostic pass, not a delivery gate. See [PowerPoint compatibility](reference/powerpoint-compatibility.md) for existing-file repairs and final merged-deck checks.

**Phase 5 — 校验 · 新眼睛 QA 🔒🔒**
- 🔒 Generator-based output requires build.py GATE PASS; direct PPTX edits require equivalent package/content checks and rendered affected-page verification.
- 🔒 On the rendered image, run a **fresh-eyes QA** pass — in Claude Code spawn the **`slide-qa`** subagent (installed by `setup.py`); fallback ladder in `reference/qa-prompt.md`. Fix → rerun `build.py` → repeat until a clean pass. Walk `reference/self-check.md`.
- 💡 *Optional (only if the page is clean-but-flat):* offer a 3-dim **polish-grade review** via the **`slide-critic`** subagent (or template) — see `reference/optional-passes.md` §A. It's a ceiling-raiser, **not a gate**.

**Phase 6 — 交付**
- Deliver a **standalone `.pptx`** to the working folder. Use the latest user-edited deck as input for requested local edits; preserve unrelated content and write a new version unless replacing the specified file is authorized.

## Verify the skill works
Run the self-test (exercises the whole chain on this machine):
```
python scripts/selftest.py        (Windows wrapper: pwsh -NoProfile -File scripts/selftest.ps1)
```
Expect `RESULT: ALL PASS ✓` across 6 steps (generate → postprocess → house checks → validate → LibreOffice render → Chrome shoot), plus two image paths to eyeball. Any FAIL points at a wrong path in `config/env.json` (rerun `python scripts/setup.py`).
Every delivered page needs successful applicable checks and rendered-page QA. Local PPTX edits do not require HTML regeneration or a generator-only GATE PASS label.

## Files
- `config/theme.json` — 🎨 palette, fonts, title spec, gradient map, layout. **Edit this to re-skin.** (`theme.deloitte/pwc/ey.json` = other built-in styles.)
- `config/env.json` — tool paths (node modules, soffice, chrome, pdftoppm, validate/unpack). Generated per machine by `scripts/setup.py`.
- `reference/` — `workflow.md`, `house-style.md`, `title-spec.md`, `gradient-landing.md`, `pitfalls.md`, `self-check.md`, `qa-prompt.md`, `design-principles.md` (frontend-design distillation for other harnesses), `optional-passes.md` (opt-in extras — hint-only, not gates).
- `templates/` — `visualizer.html` (HTML mockup skeleton), `gen_template.js` (pptxgenjs house template).
- `scripts/` — Python is the canonical cross-platform layer: `setup.py`, `selftest.py`, `build.py` (⭐ the one-shot gate), `shoot.py` (HTML→PNG), `render.py` (pptx→images), `postprocess.py`, `check_pptx.py` (bundled MIT validator + house checks), `extract_deck_style.py`, `sample_color.js`, `capture_palette.js`. The `.ps1` files are thin Windows wrappers.
- `agents/` — `slide-qa.md` (Phase-5 QA gate) and `slide-critic.md` (optional polish pass) subagent definitions; `setup.py` installs them to `~/.claude/agents/`.

## Requirements & portability
- Needs Node + Python 3 + LibreOffice + Chrome + poppler; the QA gate reads rendered images, so the agent/model must have **vision**.
- Non-Claude-Code harnesses: everything above is plain Markdown + Python/Node — follow this file top-to-bottom. Where it names Claude Code tools (AskUserQuestion, subagents `slide-qa`/`slide-critic`), degrade gracefully: plain-text questions, and the QA fallback ladder in `reference/qa-prompt.md`. See root `AGENTS.md`.

## Hard rules (red lines)
- PowerPoint automation is permitted for compatibility QA on unique temporary copies: read, export, save a temporary copy, close/reopen that copy. Never change global alert/security settings, quit the user's application, close their existing documents, or overwrite the source as part of QA. Other edits follow the user's authorized scope.
- Respect the mode and direction already established; preserve the brief approval for new or changed directions, without repeating it for local edits.
- No gold; no footer summary bar.
- Gradients/atmosphere must be **editable surface fills** (placeholder→gradFill), never baked into images or the slide background.
- Business-formal copy, no AI-isms / slogans; keep standard domain terms, never invent examples.
- Complete the validation path appropriate to generation or targeted PPTX editing, and obtain a clean rendered-page QA result before declaring done.
