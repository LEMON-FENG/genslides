# -*- coding: utf-8 -*-
"""
genslides · screenshot an HTML mockup with Chrome headless (1280x720 @2x).
Cross-platform canonical implementation (shoot.ps1 is a thin wrapper).

Usage: python shoot.py <page.html> [out.png]
"""
import os
import pathlib
import sys

from _common import load_env, need, run, utf8_stdout


def main():
    utf8_stdout()
    if len(sys.argv) < 2:
        sys.exit("usage: python shoot.py <page.html> [out.png]")
    html = os.path.abspath(sys.argv[1])
    if not os.path.exists(html):
        sys.exit("html not found: %s" % html)
    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.splitext(html)[0] + ".png"

    env = load_env()
    chrome = need(env, "chrome")
    uri = pathlib.Path(html).as_uri()
    rc, log = run([
        chrome, "--headless", "--disable-gpu",
        "--force-device-scale-factor=2", "--window-size=1280,720",
        "--hide-scrollbars", "--default-background-color=00000000",
        "--screenshot=%s" % out, uri,
    ])
    if not os.path.exists(out):
        sys.exit("screenshot failed (rc=%d)\n%s" % (rc, log.strip()))
    print("shot -> %s" % out)


if __name__ == "__main__":
    main()
