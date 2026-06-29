# House style (default: KPMG)

The default brand standard is **KPMG** (navy `00338D` / blue `0091DA` / 微软雅黑 / 「主题：阐述」titles). All colors/fonts/sizes live in `config/theme.json` and are configurable to any brand. This doc explains the *rules*; the values come from the config.

## Palette discipline
- One color dominates (primary), one supporting (accent), one sharp accent; never give all equal weight.
- Light backgrounds for content; reserve a dark band for the title/start/result anchor.
- **No gold** (`forbidden.gold`). **No footer summary bar.**

## Typography
- East-Asian glyphs use `fonts.eastasian`; latin/digits use `fonts.latin`. (pptxgenjs fills all three font slots the same → fixed by `postprocess.py`.)
- Sizes: slide title 20–24pt bold; section header 12–14pt bold; body 9–11pt; captions 8–9pt muted.

## Title / subtitle
See `reference/title-spec.md`. Default: 一级「主题：阐述」冒号式 + 二级一句正式商务. No eyebrow/kicker, no fancy `charSpacing`. Covers / TOC / section-divider pages keep their original treatment.

## Copy (文案)
- Business-formal, readable by both finance and IT. **Remove AI-isms and slogans** ("一体 / 闭环 / 前置闸口 / 赋能 / 三场景一体" and the like). Use complete, restrained sentences.
- Keep standard domain terms intact (accounting/ERP/standards vocabulary); only strip self-invented jargon.
- **Never invent example numbers or facts.** Use the user's real data; if data is illustrative, label it.
- Title pattern example: `主题：明晰现状短板，构建统一全场景能力`.

## Layout
- 16:9 = `layout.widthIn` × `layout.heightIn` (13.333×7.5"); margins `layout.marginIn`.
- HTML mockup = `layout.html` (1280×720, margin 42px). 1px ≈ 1/96 inch when mapping HTML→pptx.
- Parametric anchors only — derive every coordinate from a few variables so one change cascades. Compute the vertical budget before writing the full generator.

## Components (house vocabulary)
- Rounded card + thin border + soft shadow (`mkShadow()` factory — never share a shadow object across calls).
- Colored header strip with a left accent bar; icon in a small colored circle/rounded-square.
- Pill/chip tags (rounded rect, pale fill or solid-primary "key" variant).
- Two-tone arrows: a single `homePlate` shape (solid) — or rectangle body + a 90°-rotated `ISOSCELES_TRIANGLE` head — to stay seamless across renderers.
- Numeric tables: one right-rail per column; signed magnitudes colored (negative = `palette.negative`); a direction chip (＋/－/±) in a *fixed* column when teaching adjustment logic — never a chip glued to a signed number (reads as a double sign).
