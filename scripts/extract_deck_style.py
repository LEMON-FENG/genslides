# -*- coding: utf-8 -*-
"""
genslides · report a deck's real title/subtitle formatting so you can unify it
into config/theme.json.title. Reads theme clrScheme, master titleStyle, and each
layout's title + body placeholder defRPr (size/color/bold).

Usage: python extract_deck_style.py <deck.pptx>
Tip: dark titles often come from layout override = schemeClr tx1 (black), not the
master navy. When ambiguous, render and use sample_color.js on the title strip.
"""
import sys, re, zipfile

def t(x):  # strip namespace, collapse
    return x

def scheme_map(theme_xml):
    # order: dk1, lt1, dk2, lt2, accent1..6, hlink, folHlink
    keys = ["dk1","lt1","dk2","lt2","accent1","accent2","accent3","accent4","accent5","accent6"]
    block = re.search(r"<a:clrScheme.*?</a:clrScheme>", theme_xml, re.S)
    m = {}
    if not block: return m
    items = re.findall(r"<a:(dk1|lt1|dk2|lt2|accent[1-6])>(.*?)</a:\1>", block.group(0), re.S)
    for name, body in items:
        srgb = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', body)
        sysc = re.search(r'<a:sysClr [^>]*lastClr="([0-9A-Fa-f]{6})"', body)
        m[name] = (srgb or sysc).group(1).upper() if (srgb or sysc) else "?"
    # map tx1->dk1, tx2->dk2, bg1->lt1, bg2->lt2
    m["tx1"], m["tx2"], m["bg1"], m["bg2"] = m.get("dk1","?"), m.get("dk2","?"), m.get("lt1","?"), m.get("lt2","?")
    return m

def color_of(rpr, sm):
    srgb = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', rpr)
    if srgb: return "#" + srgb.group(1).upper()
    sch = re.search(r'<a:schemeClr val="(\w+)"', rpr)
    if sch: return "%s(%s)" % (sch.group(1), sm.get(sch.group(1), "?"))
    return "(inherited)"

def first_defrpr(sp_xml):
    m = re.search(r"<a:defRPr\b[^>]*>.*?</a:defRPr>|<a:defRPr\b[^>]*/>", sp_xml, re.S)
    return m.group(0) if m else ""

def attr(rpr, name):
    m = re.search(r'\b%s="([^"]+)"' % name, rpr)
    return m.group(1) if m else "-"

def ph_blocks(xml):
    # return list of (ph_type, ph_idx, sp_xml) for shapes carrying a placeholder
    out = []
    for sp in re.findall(r"<p:sp>.*?</p:sp>", xml, re.S):
        ph = re.search(r'<p:ph\b([^>]*)/?>', sp)
        if not ph: continue
        a = ph.group(1)
        ty = re.search(r'type="(\w+)"', a); idx = re.search(r'idx="(\d+)"', a)
        out.append((ty.group(1) if ty else "(body)", idx.group(1) if idx else "-", sp))
    return out

def main():
    if len(sys.argv) < 2:
        print("usage: python extract_deck_style.py <deck.pptx>"); sys.exit(2)
    z = zipfile.ZipFile(sys.argv[1], "r")
    names = z.namelist()
    theme = next((n for n in names if re.match(r"ppt/theme/theme\d+\.xml", n)), None)
    sm = scheme_map(z.read(theme).decode("utf-8")) if theme else {}
    print("clrScheme:", {k: sm.get(k) for k in ["dk1","lt1","dk2","lt2","accent1"]})
    print("  tx1=%s  tx2=%s  accent1=%s" % (sm.get("tx1"), sm.get("tx2"), sm.get("accent1")))

    # master titleStyle
    for n in sorted(x for x in names if re.match(r"ppt/slideMasters/slideMaster\d+\.xml", x)):
        xml = z.read(n).decode("utf-8")
        ts = re.search(r"<p:titleStyle>.*?</p:titleStyle>", xml, re.S)
        if ts:
            rpr = first_defrpr(ts.group(0))
            print(f"\n[{n}] titleStyle defRPr: sz={attr(rpr,'sz')} b={attr(rpr,'b')} color={color_of(rpr, sm)}")

    # layouts: title + body placeholders
    for n in sorted(x for x in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml", x)):
        xml = z.read(n).decode("utf-8")
        rows = []
        for ty, idx, sp in ph_blocks(xml):
            rpr = first_defrpr(sp)
            if not rpr: continue
            rows.append(f"    ph type={ty} idx={idx}: sz={attr(rpr,'sz')} b={attr(rpr,'b')} color={color_of(rpr, sm)}")
        if rows:
            print(f"\n[{n}]")
            print("\n".join(rows[:6]))
    print("\nNote: sz is in 1/100 pt (2000 = 20pt). title color schemeClr tx1 => black; tx2 => dk2/navy.")

if __name__ == "__main__":
    main()
