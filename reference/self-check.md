# Pre-delivery self-check

Walk every box before declaring done.

## Process gates
- [ ] Phase 0: asked the user ①optimize-current vs ②rebuild — didn't assume.
- [ ] Phase 2: HTML mockup screenshot shown; for ②, direction variants offered and one chosen.
- [ ] Phase 1: if domain facts involved, verified against authoritative sources; listed standard vs. extended items.

## Build
- [ ] Colors/fonts/title sizes come from `config/theme.json`.
- [ ] All pptxgenjs hex colors without `#`.
- [ ] Parametric coordinates; vertical budget computed; nothing overlaps/overflows.
- [ ] Gradients are placeholder→gradFill (editable), not images/background. Large areas solid.
- [ ] No gold; no footer summary bar.
- [ ] Copy is business-formal, no AI-isms/slogans, real (not invented) data, standard terms kept.

## Build gate 🔒
- [ ] `python scripts/build.py gen_page.js page.pptx` → **GATE PASS** (generate → postprocess → house checks → validate → render, one atomic command).
- [ ] Rerun after the *last* change to generator/theme — the delivered file is the one that passed.
- [ ] Rendered image eyeballed.

## Fresh-eyes QA 🔒
- [ ] QA pass run on the render — `slide-qa` subagent in Claude Code, else the `qa-prompt.md` fallback ladder; issues fixed; affected area re-verified; a full clean pass achieved.

## Delivery
- [ ] Standalone `.pptx` written to the working folder; the user's live deck untouched.
- [ ] `*.html` + screenshot + `gen_*.js` kept beside it as the page's source of truth.
