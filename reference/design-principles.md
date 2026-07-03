# Design principles (frontend-design distillation)

The HTML-mockup stage (Phase 2) normally composes Anthropic's `frontend-design` skill. On a harness where that skill isn't installed, apply this distillation instead — **never skip the design pass**. It keeps the skill's transferable judgment, re-scoped for a locked-brand consulting slide (where the original's "pick wild fonts / extreme tones" advice does NOT apply — fonts and palette come from `config/theme.json`).

## Commit to one clear direction
- Before writing CSS, decide the page's single organizing idea (matrix? main axis? layered funnel?) and its **one focal point** — the element a reader should see first. Execute that idea with precision; intentionality beats intensity.
- Ask: what makes this page memorable *within a formal deck*? Usually one strong structural move (a dominant band, an oversized key figure, a clean two-column tension) — not decoration.

## Hierarchy & composition
- One element dominates; everything else supports. If everything is the same weight, the page is flat (this is exactly what the optional `slide-critic` pass grades).
- Use asymmetry and controlled density deliberately: generous whitespace around the focal point, tighter rhythm in supporting grids. Align to a few strong rails rather than scattering boxes.
- Repeat one motif (chip shape, accent bar, icon circle) 2–3 times to make the page cohere.

## Color discipline (house-constrained)
- Dominant + sharp accent outperforms an evenly-distributed palette: `palette.primary` anchors, `palette.accent` points, everything else stays quiet. Never give three colors equal area.
- Light content surfaces; reserve the dark band for the title/result anchor. All values from `theme.json` — never invent brand colors from memory.

## Atmosphere & depth (within editable-fill limits)
- Avoid dead flat: soft shadows, thin borders, pale fills, and *small* gradient accents create depth. In HTML gradients are free; in pptx they must land as placeholder→gradFill (see `gradient-landing.md`) — so put gradients only where that technique supports them (small tiles/strips/badges).
- No baked-image backgrounds, no full-bleed gradient washes — the deliverable must stay editable.

## Typography (house-constrained)
- Fonts are fixed (`fonts.eastasian` / `fonts.latin`) — differentiation comes from **size contrast and weight**, not typeface: big bold key figures vs. quiet 9–11pt body, per `house-style.md` sizes.
- Line-height and box padding are design decisions; cramped text reads cheap.

## Anti-slop checklist
- No cookie-cutter "three equal cards + icon" layout unless the content genuinely is three equal items.
- No decoration that encodes nothing (random dots, unexplained arrows).
- No purple-gradient-on-white or other off-brand cliché; no gold (`forbidden.gold`).
- Every visual element should answer "what does this encode?" — if nothing, delete it.
