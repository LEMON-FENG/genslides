# -*- coding: utf-8 -*-
"""
genslides · one-shot build gate (cross-platform).
Chains generate -> postprocess -> validate (house + configured) -> render as ONE
atomic command: any step failing exits nonzero. This is the machine-checkable 🔒 —
a page ships only if this prints GATE PASS.

Usage: python build.py <gen_page.js> [out.pptx] [--theme=config/theme.<brand>.json] [--no-render]

Steps:
  1 generate     node <gen_page.js> <out.pptx>       (NODE_PATH + GENSLIDES_THEME set)
  2 postprocess  fonts + notesMasterIdLst + strip dir entries + gradient placeholders
  3 house checks bundled check_pptx.py (PowerPoint "needs repair" causes, leftover
                 EE00xx placeholders, '#' in hex)
  4 validate     configured env.json validatePy, if present and different (full XSD)
  5 render       LibreOffice -> JPG(s), paths printed for eyeballing / fresh-eyes QA
"""
import os
import sys

from _common import HERE, ROOT, load_env, run, utf8_stdout


def step(name, ok, detail=""):
    print("%-14s [%s] %s" % (name, "PASS" if ok else "FAIL", detail))
    return ok


def tail(log, n=3):
    lines = [l for l in log.strip().splitlines() if l.strip()]
    return " | ".join(lines[-n:])


def main():
    utf8_stdout()
    args = sys.argv[1:]
    theme = None
    render = True
    pos = []
    for a in args:
        if a.startswith("--theme="):
            theme = a.split("=", 1)[1]
        elif a == "--no-render":
            render = False
        else:
            pos.append(a)
    if not pos:
        sys.exit("usage: python build.py <gen_page.js> [out.pptx] [--theme=<theme.json>] [--no-render]")

    gen_js = os.path.abspath(pos[0])
    if not os.path.exists(gen_js):
        sys.exit("generator not found: %s" % gen_js)
    out = os.path.abspath(pos[1]) if len(pos) > 1 else os.path.splitext(gen_js)[0] + ".pptx"

    # resolve theme explicitly and always pass it down — copied gen_*.js live in
    # working folders where their own __dirname-relative fallback can't find config/
    if theme:
        cand = theme if os.path.exists(theme) else os.path.join(ROOT, theme)
        if not os.path.exists(cand):
            sys.exit("theme not found: %s" % theme)
        theme = os.path.abspath(cand)
    else:
        theme = os.path.join(ROOT, "config", "theme.json")

    env = load_env()
    ok = True

    # 1 generate
    extra = {"NODE_PATH": env.get("nodeModules", ""), "GENSLIDES_THEME": theme}
    rc, log = run(["node", gen_js, out], extra_env=extra)
    ok &= step("1 generate", rc == 0 and os.path.exists(out), tail(log, 1))
    if not ok:
        print(log.strip())
        return finish(False)

    # 2 postprocess
    rc, log = run([sys.executable, os.path.join(HERE, "postprocess.py"), out, theme])
    ok &= step("2 postprocess", rc == 0 and "DONE" in log, tail(log))
    if not ok:
        print(log.strip())
        return finish(False)

    # 3 house checks (bundled — always run; catches what XSD tools tolerate)
    house = os.path.join(HERE, "check_pptx.py")
    rc, log = run([sys.executable, house, out])
    ok &= step("3 house checks", rc == 0 and "All validations PASSED" in log, tail(log, 6))

    # 4 configured validator (stronger XSD), if present and not the same file
    validator = env.get("validatePy")
    if validator and os.path.exists(validator) and os.path.normcase(os.path.abspath(validator)) != os.path.normcase(house):
        rc, log = run([sys.executable, validator, out])
        ok &= step("4 validate", rc == 0 and "All validations PASSED" in log,
                   "via " + os.path.basename(validator) + " | " + tail(log, 2))
    else:
        print("%-14s [SKIP] no separate validator configured (house checks already ran)" % "4 validate")
    if not ok:
        return finish(False)

    # 5 render (for eyeballing + the fresh-eyes QA pass)
    if render:
        rc, log = run([sys.executable, os.path.join(HERE, "render.py"), out])
        jpgs = [l for l in log.strip().splitlines() if l.strip().lower().endswith(".jpg")]
        ok &= step("5 render", rc == 0 and bool(jpgs), jpgs[0] if jpgs else tail(log))
        for j in jpgs[1:]:
            print(" " * 22 + j)
    else:
        print("%-14s [SKIP] --no-render" % "5 render")

    return finish(ok, out)


def finish(ok, out=None):
    print()
    if ok:
        print("GATE PASS  ✓  %s" % (out or ""))
        sys.exit(0)
    print("GATE FAIL  ✗  fix and rerun — do NOT deliver this page")
    sys.exit(1)


if __name__ == "__main__":
    main()
