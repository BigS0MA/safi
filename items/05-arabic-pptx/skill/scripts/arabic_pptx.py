#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Arabic in a PowerPoint file (.pptx): right-to-left paragraphs and bullets, correct order around
English words, Arabic the same size and font as English, tables from the right.

  python3 arabic_pptx.py in.pptx            → in_fixed.pptx
  python3 arabic_pptx.py in.pptx out.pptx

Works on decks made by ChatGPT, Claude or any script (python-pptx, pptxgenjs), and on decks that are
already broken. Only direction, alignment, language and font properties change; the text is never touched.
Needs: pip install python-pptx
"""
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree

ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
A = lambda tag: qn(f"a:{tag}")
# CT_TextCharacterProperties child order: … latin, ea, cs, sym, hlinkClick, hlinkMouseOver, rtl, extLst
AFTER_CS = {A(t) for t in ("sym", "hlinkClick", "hlinkMouseOver", "rtl", "extLst")}


def _text(p):
    return "".join(t.text or "" for t in p.iter(A("t")))


def fix_paragraph(p):
    """p is an <a:p>."""
    if not ARABIC.search(_text(p)):
        return False
    pPr = p.find(A("pPr"))
    if pPr is None:
        pPr = etree.SubElement(p, A("pPr"))
        p.remove(pPr)
        p.insert(0, pPr)
    pPr.set("rtl", "1")
    if pPr.get("algn") in (None, "l"):          # PowerPoint alignment is absolute: right stays right in RTL
        pPr.set("algn", "r")
    for rPr in list(p.iter(A("rPr"))) + list(p.iter(A("endParaRPr"))):
        fix_run_props(rPr)
    return True


def fix_run_props(rPr):
    if rPr.get("lang") in (None, "en-US", "en-GB") and rPr.tag == A("rPr"):
        r = rPr.getparent()
        t = r.find(A("t")) if r is not None else None
        if t is not None and ARABIC.search(t.text or ""):
            rPr.set("lang", "ar-JO")
    latin = rPr.find(A("latin"))
    if latin is not None and rPr.find(A("cs")) is None:      # Arabic uses the complex-script font slot
        cs = etree.Element(A("cs"))
        cs.set("typeface", latin.get("typeface"))
        ea = rPr.find(A("ea"))
        (ea if ea is not None else latin).addnext(cs)


def fix_tables(root):
    for tblPr in root.iter(A("tblPr")):
        tbl = tblPr.getparent()
        if ARABIC.search("".join(t.text or "" for t in tbl.iter(A("t")))):
            tblPr.set("rtl", "1")                            # first column on the right (PowerPoint)
            for para in tbl.iter(A("p")):                    # numbers / English cells follow the table
                pPr = para.find(A("pPr"))
                if pPr is None:
                    pPr = etree.Element(A("pPr"))
                    para.insert(0, pPr)
                pPr.set("rtl", "1")
                if pPr.get("algn") in (None, "l"):
                    pPr.set("algn", "r")


def fix(path_in, path_out=None):
    prs = Presentation(path_in)
    n = 0
    parts = [s._element for s in prs.slides]
    parts += [l._element for l in prs.slide_layouts] + [prs.slide_master._element]
    for el in parts:
        for p in el.iter(A("p")):
            n += fix_paragraph(p)
        fix_tables(el)
    out = Path(path_out) if path_out else Path(path_in).with_name(Path(path_in).stem + "_fixed.pptx")
    prs.save(out)
    return out, n


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out, n = fix(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"✅ {n} فقرة عربية انصلحت → {out}")
