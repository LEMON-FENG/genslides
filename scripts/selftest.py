# -*- coding: utf-8 -*-
"""
genslides · self-test (cross-platform canonical; selftest.ps1 is a thin wrapper).
Exercises the whole chain on the bundled template: build gate (generate ->
postprocess -> house checks -> validate -> render) + Chrome shoot.

Usage: python scripts/selftest.py        → RESULT: ALL PASS ✓ / SOME FAIL ✗ (exit 0/1)
"""
import os
import subprocess
import sys
import tempfile
import uuid

from _common import HERE, ROOT, utf8_stdout


def main():
    utf8_stdout()
    work = os.path.join(tempfile.gettempdir(), "genslides_selftest_" + uuid.uuid4().hex[:6])
    os.makedirs(work, exist_ok=True)
    pptx = os.path.join(work, "selftest.pptx")

    # steps 1-5: the one-shot build gate on the bundled template
    rc = subprocess.call([
        sys.executable, os.path.join(HERE, "build.py"),
        os.path.join(ROOT, "templates", "gen_template.js"), pptx,
    ])
    ok = rc == 0

    # step 6: shoot the HTML mockup (Chrome headless)
    png = os.path.join(work, "viz.png")
    rc = subprocess.call([
        sys.executable, os.path.join(HERE, "shoot.py"),
        os.path.join(ROOT, "templates", "visualizer.html"), png,
    ])
    shot = rc == 0 and os.path.exists(png)
    print("%-14s [%s] %s" % ("6 shoot", "PASS" if shot else "FAIL", png))
    ok = ok and shot

    print()
    if ok:
        jpg = os.path.join(work, "selftest-1.jpg")
        print("RESULT: ALL PASS  ✓   eyeball -> %s  and  %s" % (jpg, png))
    else:
        print("RESULT: SOME FAIL ✗   check config/env.json paths (or rerun scripts/setup.py)")
    try:
        os.remove(pptx)
    except OSError:
        pass
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
