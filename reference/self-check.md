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

## Post-process
- [ ] Font slots fixed (latin/cs = latin font; ea = eastasian; no leftover).
- [ ] `notesMasterIdLst` moved before `sldIdLst`.

## Validation 🔒
- [ ] `validate.py` → **"All validations PASSED!"** (re-run after gradient post-process).
- [ ] Rendered to image and eyeballed.
- [ ] **Fresh-eyes QA subagent** run (`qa-prompt.md`); issues fixed; affected slide re-verified; a full clean pass achieved.

## Delivery
- [ ] Standalone `.pptx` written to the working folder; the user's live deck untouched.
- [ ] `*.html` + screenshot + `gen_*.js` kept beside it as the page's source of truth.
