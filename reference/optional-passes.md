# Optional passes (opt-in — NOT gates)

Two techniques borrowed (and trimmed) from the `huashu-design` skill. **They are not part of the default flow.** The default remains the 4 gates in `workflow.md`. These two are invoked **only in special cases**.

> **Agent behavior: HINT, don't auto-run.** At the relevant phase, *mention* that the pass is available and when it would help — then let the user ask for it. Never run either by default; never let them block delivery.

Why trimmed / opt-in:
- The **fresh-eyes bug-hunt** (`qa-prompt.md`) stays the real QA gate. It catches objective defects (collisions, misalignment, double-signs, package errors) that a design-grade rubric can't.
- These two answer different questions: the polish review grades "good vs. flat" (a ceiling-raiser), and parallel variants explore "which direction" (earlier, at design time). Neither replaces defect detection.

---

## A. Polish-grade review (Phase 5, optional — after bug-QA passes)

**When to offer it:** the page passes the fresh-eyes bug-hunt (no defects) but reads **"clean but flat"** — no focal point, everything the same weight, generic. Use it to raise the ceiling. **Not a gate; does not block delivery.**

**What's trimmed vs. huashu's 5-dim:** dropped **创新/innovation** (actively harmful for a standard financial/consulting deliverable — you don't want an "innovative" cash-flow schedule), and folded 功能性/细节 into the bug-hunt. Left with 3 dimensions that the bug-hunt does *not* score:

1. **视觉层级 (visual hierarchy)** — is there one clear focal point? does the title / key number dominate, or is it all one weight?
2. **品牌口径一致性 (brand & house consistency)** — colors/fonts/title format match `config/theme.json` and the target deck? terminology standard, not invented?
3. **细节执行 (detail execution)** — number rails, spacing rhythm, optical alignment, micro-polish *beyond* "no bugs".

**Output:** each scored 0–10 with one line of reasoning, then **Keep / Fix / Quick-Wins**. Treat it as a polish TODO, not pass/fail.

**Subagent prompt template:**
```
You are a senior presentation design critic. This slide already passed defect QA — do NOT hunt for bugs. Grade its DESIGN QUALITY for a high-end consulting/bid deck on three dimensions, 0–10 each, with one line of why:
  1. 视觉层级 — clear focal point? does the title/key figure dominate, or is everything the same weight?
  2. 品牌口径一致性 — consistent palette/fonts/title format; standard terminology; would it sit seamlessly in the rest of the deck?
  3. 细节执行 — number rails, spacing rhythm, optical alignment, micro-polish.
Image: {ABSOLUTE_PATH}
Context: {ONE_LINE — what the page is and where it goes}
End with: Keep (what's already strong) / Fix (highest-impact change) / Quick-Wins (≤3 small tweaks). Do not invent defects; if a dimension is already strong, say 9–10 and move on.
```

---

## B. Parallel direction variants (Phase 2, optional — ②rebuild only)

**When to offer it:** mode is **②rebuild** *and* the design space is genuinely open (several viable structures). **Skip** for ①optimize, or when one layout is obviously right — don't fan out for the sake of it.

**How:** spawn 2–3 subagents, each builds a **different** HTML direction from the *same* content/spec (e.g. `page_甲.html` 矩阵 / `page_乙.html` 主轴 / `page_丙.html` 分层), screenshot each (`shoot.ps1`), present side-by-side, user picks one → proceed to pptxgenjs on the winner.

**Why it helps:** beats anchoring on the first idea. It's an *exploration* step (upstream of QA), not a verification step — it doesn't compete with the bug-hunt.

---

## C. Style / brand capture (Phase 1, optional — non-KPMG only)

**Default is always KPMG.** The first cut is built on `config/theme.json` (KPMG navy/blue) — do NOT run capture by default. **Only offer it** when the user says, in effect, *"use a different palette / brand"* or *"match this brand-new template"*. (Brand-capture idea borrowed from huashu-design's Brand Asset Protocol, trimmed.)

**Sources:** a reference deck (`.pptx`), a brand screenshot / logo / poster image, or a brand site page.

**Flow (never guess brand colors from memory — sample them):**
1. Get an image of the source (render a deck with `scripts/render.ps1`; or use the screenshot/logo directly; or a screenshot of the brand page).
2. **Palette:** `node scripts/capture_palette.js <image>` → frequency-ranked saturated brand colors + light tints + a heuristic role guess (primary / accent / paleBg). **Verify** the guess by eye.
3. **Title/subtitle format** (if the source is a deck): `python scripts/extract_deck_style.py <deck.pptx>` → title/subtitle size & color.
4. **Codify:** copy `config/theme.json` → `config/theme.<brand>.json`, replace `palette.*` and `title.*` with the verified values. **Leave the default `theme.json` (KPMG) untouched.**
5. **Generate against it:** set env `GENSLIDES_THEME=config/theme.<brand>.json` before `node gen_*.js` (and the same for `postprocess.py` if its gradient map changed). Everything downstream re-skins automatically.

**Rule:** first version = KPMG. Switch brands only on explicit request, via a *separate* theme file — the KPMG default stays the fallback.

---

**All three are optional.** If the user doesn't ask, run the normal 4-gate flow on the default KPMG theme.
