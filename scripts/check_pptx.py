# -*- coding: utf-8 -*-
"""
genslides · self-contained .pptx structural validator (MIT, stdlib only).
Catches the failure modes that make PowerPoint say "needs repair" but which
LibreOffice / markitdown silently tolerate — without depending on the
proprietary `pptx` skill. For full XSD schema validation, point env.json's
validatePy at the `pptx` skill's validate.py instead (stronger, optional).

Checks: (1) no stray zip directory entries, (2) all XML/.rels well-formed,
(3) presentation.xml has notesMasterIdLst before sldIdLst, (4) every .rels
target resolves, (5) every part is covered by [Content_Types].xml.

Usage: python check_pptx.py <file.pptx>   → prints "All validations PASSED!" + exit 0, or errors + exit 1.
"""
import sys, zipfile, posixpath
import xml.etree.ElementTree as ET


def main():
    if len(sys.argv) < 2:
        print("usage: python check_pptx.py <file.pptx>"); sys.exit(2)
    path = sys.argv[1]
    errors = []
    z = zipfile.ZipFile(path)
    names = z.namelist()
    files = [n for n in names if not n.endswith("/")]

    # 1) stray directory entries → PowerPoint "needs repair"
    dirs = [n for n in names if n.endswith("/")]
    if dirs:
        errors.append("%d stray directory entr%s in package (PowerPoint repair): %s%s"
                      % (len(dirs), "y" if len(dirs) == 1 else "ies", ", ".join(dirs[:4]),
                         " …" if len(dirs) > 4 else ""))

    # 2) well-formed XML
    for n in files:
        if n.endswith(".xml") or n.endswith(".rels"):
            try:
                ET.fromstring(z.read(n))
            except Exception as e:
                errors.append("malformed XML in %s: %s" % (n, e))

    # 3) presentation.xml element order: notesMasterIdLst before sldIdLst
    pres = "ppt/presentation.xml"
    if pres in files:
        t = z.read(pres).decode("utf-8", "replace")
        nm, sl = t.find("notesMasterIdLst"), t.find("sldIdLst")
        if nm != -1 and sl != -1 and nm > sl:
            errors.append("presentation.xml: notesMasterIdLst is after sldIdLst (PowerPoint repair); must be before")

    # 4) relationship targets resolve
    for n in files:
        if not n.endswith(".rels"):
            continue
        part_base = posixpath.dirname(posixpath.dirname(n))  # parent of the _rels/ folder
        try:
            root = ET.fromstring(z.read(n))
        except Exception:
            continue
        for rel in root:
            tgt = rel.get("Target")
            if not tgt or rel.get("TargetMode") == "External" or tgt.startswith("http"):
                continue
            resolved = posixpath.normpath(posixpath.join(part_base, tgt))
            if resolved not in files:
                errors.append("dangling relationship in %s -> %s" % (n, tgt))

    # 5) [Content_Types].xml coverage
    ct = "[Content_Types].xml"
    if ct in files:
        root = ET.fromstring(z.read(ct))
        defaults, overrides = set(), set()
        for el in root:
            tag = el.tag.split("}")[-1]
            if tag == "Default":
                defaults.add((el.get("Extension") or "").lower())
            elif tag == "Override":
                overrides.add(el.get("PartName") or "")
        for n in files:
            if n == ct:
                continue
            ext = n.rsplit(".", 1)[-1].lower() if "." in n else ""
            if ("/" + n) not in overrides and ext not in defaults:
                errors.append("part not covered by [Content_Types].xml: %s" % n)
    z.close()

    if errors:
        print("VALIDATION FAILED (%d issue%s):" % (len(errors), "" if len(errors) == 1 else "s"))
        for e in errors[:30]:
            print("  -", e)
        sys.exit(1)
    print("All validations PASSED!")


if __name__ == "__main__":
    main()
