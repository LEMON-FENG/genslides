---
name: genslides
description: Produce a single high-quality, on-brand presentation slide (.pptx) using an HTML-mockup-first → pptxgenjs → validate workflow. Ships with four built-in Big-Four consulting styles (KPMG by default, plus Deloitte / PwC / EY), switchable in config/theme.json and configurable to any brand. Use when asked to design, beautify, or rebuild a deck page for consulting / bid / executive decks — 触发语示例：美化/重做/设计这一页 slide、做一页咨询/述标风格的 pptx 样品页、把这张表做成顾问风格、把这页做漂亮. Composes the `pptx` and `frontend-design` skills (bundled fallbacks included for other harnesses) and enforces four gates - mode-alignment, HTML direction sign-off, one-shot build validation (GATE PASS), and fresh-eyes QA. Keep end-client names out of the skill.
argument-hint: "[①优化|②重构] [--theme=kpmg|deloitte|pwc|ey]"
allowed-tools: Bash(node:*), Bash(python:*), Bash(pwsh:*)
---

# genslides

A reusable workflow for crafting **one polished slide at a time**, then delivering it as a standalone `.pptx` the user merges into their master deck by hand. Ships with **four built-in Big-Four consulting styles** — **KPMG** (default) · **Deloitte** · **PwC** · **EY** — switchable via `config/theme.json`, and configurable to any brand.

The defining idea: **decide the visuals on a fast HTML mockup first, sign it off, then faithfully reproduce that mockup in pptxgenjs** — never design straight in pptxgenjs. Gradients and brand colors live as *editable* fills, not baked images.

> This skill is a **living template**. `config/theme.json` is the single source of truth for the brand (default KPMG) — palette / fonts / title spec — edit it to re-skin everything. `templates/` and `scripts/` are meant to be copied and improved per engagement. Keep **end-client** names out (乐美/商米/etc.); put engagement-specific facts in the working folder, not here. The firm brand (KPMG) is the default and is fine to name.

## Arguments

Invocation may carry arguments: `$ARGUMENTS`

- `①` / `②` (or `优化` / `重构`) — pre-answers the Phase-0 mode question; skip the ask.
- `--theme=<firm>` — use `config/theme.<firm>.json` (deloitte / pwc / ey); pass it through as `scripts/build.py --theme=...`. Default is KPMG (`config/theme.json`).
- No arguments → run the normal flow (Phase 0 asks the mode).

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

**Phase 0 — 定模式 🔒 (ask, never assume)**
Unless the arguments already answer it, ask the user: is this page **① optimize-current** (keep the skeleton, minimal targeted edits, drop-in) or **② rebuild-after-aligning-direction**? In Claude Code use the **AskUserQuestion** tool (two options ①/②); other harnesses ask in plain text. For ②, you must align the *direction* first (Phase 2 gives 2–3 variants). Rule: **adoptability (fits the deck, pre-aligned) > design perfection.**

**Phase 1 — 取证 & 对口径**
- Default brand = KPMG (`config/theme.json`). Build the first cut on it. 💡 *Optional (non-KPMG only):* if the user wants a different palette/brand or to match a brand-new template, offer the **style/brand capture** pass — `reference/optional-passes.md` §C — which samples colors + title format into a *separate* `theme.<brand>.json` (KPMG default untouched). Hint it's available; don't switch brands by default.
- Render the reference deck (`python scripts/render.py deck.pptx`); study 2–3 strong pages for the visual language.
- Extract the deck's real title/subtitle format with `scripts/extract_deck_style.py`; sample a rendered pixel with `scripts/sample_color.js` when XML inheritance is ambiguous. Reconcile against `config/theme.json` → `title`.
- If the page encodes domain facts (finance/accounting/data logic), **verify against authoritative sources before drawing** and list "standard vs. extended" items. Fix errors first.

**Phase 2 — HTML 真稿 · 方向拉齐 🔒**
- Build a high-fidelity HTML mockup from `templates/visualizer.html` (1280×720, themed via CSS vars from `theme.json`). This is where **frontend-design** quality happens (fallback: `reference/design-principles.md`) — CSS gradients, `clip-path`, inline SVG icons, shadows are all free here.
- Screenshot with `python scripts/shoot.py page.html` (Chrome headless). For **②rebuild**, produce 2–3 *direction variants* (e.g. `*_甲.html / *_乙.html / *_丙.html`) and have the user pick before proceeding (AskUserQuestion in Claude Code).
- Iterate on HTML until signed off. Keep `*.html` + screenshot as the page's source of truth.
- 💡 *Optional (②rebuild, open design space):* you may fan out parallel direction variants via subagents — see `reference/optional-passes.md` §B. Mention it's available; don't fan out by default.

**Phase 3 — pptxgenjs 复刻**
- Copy `templates/gen_template.js`; reproduce the **approved** HTML faithfully. Parametric coordinates, compute heights first. See `reference/house-style.md` and `reference/pitfalls.md`.
- Small accents/tiles/badges/top-bars that need gradients get a **unique placeholder solid color**; large areas stay solid. See `reference/gradient-landing.md`.

**Phase 4 — 一键出包 🔒 (`scripts/build.py`)**
```
python scripts/build.py gen_page.js page.pptx [--theme=config/theme.<firm>.json]
```
One atomic command: generate → postprocess (font slots / notesMasterIdLst / strip dir entries / gradient placeholders→gradFill) → house checks (`check_pptx.py`) → configured `validate.py` → render to JPG. 🔒 it must end with **GATE PASS** — any step failing exits nonzero; fix and rerun. Never hand-run a partial chain and declare it validated.

**Phase 5 — 校验 · 新眼睛 QA 🔒🔒**
- 🔒 `build.py` printed **GATE PASS** (covers OOXML validation; rerun after *any* regeneration).
- 🔒 On the rendered image, run a **fresh-eyes QA** pass — in Claude Code spawn the **`slide-qa`** subagent (installed by `setup.py`); fallback ladder in `reference/qa-prompt.md`. Fix → rerun `build.py` → repeat until a clean pass. Walk `reference/self-check.md`.
- 💡 *Optional (only if the page is clean-but-flat):* offer a 3-dim **polish-grade review** via the **`slide-critic`** subagent (or template) — see `reference/optional-passes.md` §A. It's a ceiling-raiser, **not a gate**.

**Phase 6 — 交付**
- Deliver a **standalone `.pptx`** to the working folder. Never touch a deck the user is editing by hand.

## Verify the skill works
Run the self-test (exercises the whole chain on this machine):
```
python scripts/selftest.py        (Windows wrapper: pwsh -NoProfile -File scripts/selftest.ps1)
```
Expect `RESULT: ALL PASS ✓` across 6 steps (generate → postprocess → house checks → validate → LibreOffice render → Chrome shoot), plus two image paths to eyeball. Any FAIL points at a wrong path in `config/env.json` (rerun `python scripts/setup.py`).
Per-page verification is the gates themselves: every delivered page must show **GATE PASS**, a render image, and a clean fresh-eyes QA report.

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
- Never automate PowerPoint (no COM); only ever write new/standalone files.
- Never assume the edit mode — ask ①/② first (unless the arguments answered it).
- No gold; no footer summary bar.
- Gradients/atmosphere must be **editable surface fills** (placeholder→gradFill), never baked into images or the slide background.
- Business-formal copy, no AI-isms / slogans; keep standard domain terms, never invent examples.
- `scripts/build.py` must print **GATE PASS** and a fresh-eyes QA pass must come back clean before declaring done.
