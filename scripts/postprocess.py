# -*- coding: utf-8 -*-
"""
genslides postprocess: fonts + notesMasterIdLst order + gradient placeholders.
Config-driven from ../config/theme.json.

Usage:  python postprocess.py <file.pptx> [theme.json]
Then always re-run validate.py.
"""
import sys, os, re, json, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

def load_theme(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def grad_fill_xml(stops, ang):
    a, b = stops[0], stops[1]
    return (
        '<a:gradFill rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="{a}"/></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="{b}"/></a:gs>'
        f'</a:gsLst><a:lin ang="{ang}" scaled="1"/></a:gradFill>'
    )

def main():
    if len(sys.argv) < 2:
        print("usage: python postprocess.py <file.pptx> [theme.json]"); sys.exit(2)
    src = sys.argv[1]
    theme_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "config", "theme.json")
    T = load_theme(theme_path)

    latin = T["fonts"]["latin"]
    ea = T["fonts"]["eastasian"]
    angles = T["gradients"]["angles"]
    placeholders = T["gradients"]["placeholders"]

    tmp = src + ".tmp"
    shutil.copy(src, tmp)
    zin = zipfile.ZipFile(tmp, "r")
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}
    zin.close()

    ea_b = ea.encode("utf-8")
    latin_b = latin.encode("utf-8")
    grad_hits = 0
    for n in list(data.keys()):
        if n.startswith("ppt/slides/slide") and n.endswith(".xml"):
            xml = data[n]
            # 1) font slots: latin/cs -> latin font ; keep ea
            xml = xml.replace(b'<a:latin typeface="' + ea_b + b'"', b'<a:latin typeface="' + latin_b + b'"')
            xml = xml.replace(b'<a:cs typeface="' + ea_b + b'"', b'<a:cs typeface="' + latin_b + b'"')
            # 2) gradient placeholders: <a:solidFill><a:srgbClr val="EE00xx"/></a:solidFill> -> gradFill
            txt = xml.decode("utf-8")
            for ph, spec in placeholders.items():
                ang = angles[spec["angle"]] if isinstance(spec["angle"], str) else spec["angle"]
                grad = grad_fill_xml(spec["stops"], ang)
                pat = re.compile(r'<a:solidFill>\s*<a:srgbClr val="%s"\s*/>\s*</a:solidFill>' % re.escape(ph))
                txt, k = pat.subn(grad, txt)
                grad_hits += k
            data[n] = txt.encode("utf-8")

    # 3) presentation.xml: notesMasterIdLst before sldIdLst
    pn = "ppt/presentation.xml"
    if pn in data:
        p = data[pn].decode("utf-8")
        m = re.search(r"<p:notesMasterIdLst>.*?</p:notesMasterIdLst>", p, re.S)
        if m:
            block = m.group(0)
            p2 = p[:m.start()] + p[m.end():]
            idx = p2.find("</p:sldMasterIdLst>")
            if idx != -1:
                ins = idx + len("</p:sldMasterIdLst>")
                p2 = p2[:ins] + block + p2[ins:]
                data[pn] = p2.encode("utf-8")
                print("moved notesMasterIdLst before sldIdLst")

    # strip stray directory entries (pptxgenjs 4.0.x injects empty folders like
    # ppt/charts/_rels/ → PowerPoint's strict OPC loader rejects them as "needs repair";
    # LibreOffice / python-pptx / validate.py ignore them). OPC packages must contain
    # only part (file) entries.
    zout = zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED)
    dropped = 0
    for n in names:
        if n.endswith("/"):
            dropped += 1
            continue
        zout.writestr(n, data[n])
    zout.close()
    print("stripped stray directory entries:", dropped)
    os.remove(tmp)

    # report
    zc = zipfile.ZipFile(src, "r")
    s1 = zc.read("ppt/slides/slide1.xml") if "ppt/slides/slide1.xml" in zc.namelist() else b""
    zc.close()
    print("fonts: latin/cs ->", latin, "| ea kept ->", ea,
          "| leftover latin-ea:", s1.count(b'<a:latin typeface="' + ea_b + b'"'))
    print("gradients replaced:", grad_hits)
    print("DONE — now run validate.py")

if __name__ == "__main__":
    main()
