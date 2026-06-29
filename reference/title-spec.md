# Title / subtitle spec

The values live in `config/theme.json` → `title`. This is the *convention*.

## Format
- **一级主标题**: `「主题：阐述」` colon form. `主题` = the page topic; `阐述` = a short verb phrase of what this page does. Bold, `title.level1` color/size.
  - e.g. `关联交易对账：明晰现状短板，构建统一全场景对账`
  - e.g. `现金流量表间接法编制：净利润逐类调节，公式自动成表`
- **二级副标题**: one business-formal sentence, single paragraph, bold, `title.level2` color/size. States the approach/outcome in one breath.
- **封面 / 目录 / 分章页**: keep the original treatment — do not apply the content-page title format.

## Two house variants (pick one and be consistent)
A deck often contains both; "unify the titles" means converging on one.
1. **Authored/house** (default in `theme.json`): primary-navy title + accent-blue subtitle. Use this to match hand-built pptxgenjs pages.
2. **Template/placeholder**: black title (`tx1`) + a different blue subtitle (often `0070C0`, 18pt). Use this only to match the deck's untouched placeholder pages.

Decide which the target deck should standardize on (ask if unsure), then set `title.level1/level2` accordingly. `scripts/extract_deck_style.py` reports what each page actually uses.

## Extraction notes (what extract_deck_style.js looks at)
- Title placeholder size/color usually comes from the **slide layout** `defRPr` (overrides the master `titleStyle`); content titles are commonly **black** (`schemeClr tx1`) even when the master default is navy.
- Subtitle is typically a body placeholder (`idx` varies) whose `defRPr` carries the bold + color.
- `theme clrScheme`: `tx1`→dk1, `tx2`→dk2, `accent1` — resolve scheme refs to real hex.
- When inheritance is ambiguous, render and pixel-sample the title strip (`scripts/sample_color.js`); a dark title sampling ~`#060606` is black, not navy.
