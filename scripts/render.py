# -*- coding: utf-8 -*-
"""
genslides · render a .pptx to per-slide JPGs (LibreOffice -> PDF -> pdftoppm).
Cross-platform canonical implementation (render.ps1 is a thin wrapper).

Usage: python render.py <file.pptx> [outDir] [dpi]
"""
import os
import pathlib
import sys
import tempfile
import uuid

from _common import load_env, need, run, utf8_stdout


def main():
    utf8_stdout()
    if len(sys.argv) < 2:
        sys.exit("usage: python render.py <file.pptx> [outDir] [dpi]")
    pptx = os.path.abspath(sys.argv[1])
    if not os.path.exists(pptx):
        sys.exit("pptx not found: %s" % pptx)
    out_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(pptx)
    dpi = sys.argv[3] if len(sys.argv) > 3 else "150"
    os.makedirs(out_dir, exist_ok=True)

    env = load_env()
    soffice = need(env, "soffice")
    pdftoppm = need(env, "pdftoppm")

    # isolated profile so it won't clash with an open LibreOffice
    prof = os.path.join(tempfile.gettempdir(), "lo_genslides_" + uuid.uuid4().hex[:8])
    rc, log = run([
        soffice, "-env:UserInstallation=%s" % pathlib.Path(prof).as_uri(),
        "--headless", "--convert-to", "pdf", "--outdir", out_dir, pptx,
    ])
    base = os.path.splitext(os.path.basename(pptx))[0]
    pdf = os.path.join(out_dir, base + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("PDF not produced (is LibreOffice busy?) rc=%d\n%s" % (rc, log.strip()))

    rc, log = run([pdftoppm, "-jpeg", "-r", str(dpi), pdf, os.path.join(out_dir, base)])
    if rc != 0:
        sys.exit("pdftoppm failed (rc=%d)\n%s" % (rc, log.strip()))
    jpgs = sorted(
        os.path.join(out_dir, f) for f in os.listdir(out_dir)
        if f.startswith(base) and f.endswith(".jpg")
    )
    if not jpgs:
        sys.exit("no JPGs produced from %s" % pdf)
    for j in jpgs:
        print(j)


if __name__ == "__main__":
    main()
