# genslides — instructions for AI coding agents

This repository is an **agent skill** (Agent Skills format, agentskills.io). To use it:

1. Read `SKILL.md` and follow its 6-phase / 4-gate workflow exactly — mode question first, HTML mockup sign-off before any pptxgenjs code, `python scripts/build.py` must print **GATE PASS**, and a fresh-eyes QA pass on the rendered image before delivery.
2. One-time per machine: `python scripts/setup.py` (installs node deps, detects tools, writes `config/env.json`).
3. The scripts are plain Python/Node and run on Windows/macOS/Linux; the `.ps1` files are optional Windows wrappers.
4. Where `SKILL.md` names Claude-Code-specific tools, degrade gracefully:
   - `AskUserQuestion` → ask in plain text.
   - `slide-qa` / `slide-critic` subagents → follow the fallback ladder in `reference/qa-prompt.md` (generic subagent with the template, or a fresh-turn self-review).
   - `frontend-design` skill → use `reference/design-principles.md`.
5. Requirements: Node, Python 3, LibreOffice, Chrome, poppler — and a **vision-capable** model (the QA gate reads rendered images).

PowerPoint automation is permitted for compatibility QA on unique temporary copies using `scripts/powerpoint_check.py`. Do not overwrite source files, change global Office settings, quit the user's application, or close existing user documents. Prefer native QA when available; XML/LibreOffice success does not prove PowerPoint compatibility. Keep end-client names out of this repo.
