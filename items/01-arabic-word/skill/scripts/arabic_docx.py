#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Arabic in a Word file (.docx): right-to-left paragraphs, correct order around English words,
Arabic the same size as English, tables right-to-left.

  python3 arabic_docx.py in.docx            → in_fixed.docx
  python3 arabic_docx.py in.docx out.docx

Works on files made by ChatGPT, Claude or any script (python-docx, docx-js), and on files that are
already broken. It only changes direction and font properties; the text itself is never touched.
Needs: pip install python-docx
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
W = lambda tag: qn(f"w:{tag}")


# ECMA-376 element order: a new element goes before the first sibling that must come after it
AFTER = {
    "bidi": ["adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"],
    "rtl": ["cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"],
    "bidiVisual": ["tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd",
                   "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription", "tblPrChange"],
    "sect_bidi": ["rtlGutter", "docGrid", "printerSettings", "sectPrChange"],
}


def _insert(parent, tag, key=None):
    """add <w:tag/> to parent at its schema position; return it (existing one if present)."""
    el = parent.find(W(tag))
    if el is not None:
        return el
    el = OxmlElement(f"w:{tag}")
    later = {W(t) for t in AFTER[key or tag]}
    for child in parent:
        if child.tag in later:
            child.addprevious(el)
            return el
    parent.append(el)
    return el


def _after(anchor, tag):
    """add <w:tag/> right after anchor (for pairs like sz → szCs, b → bCs)."""
    el = anchor.getparent().find(W(tag))
    if el is None:
        el = OxmlElement(f"w:{tag}")
        anchor.addnext(el)
    return el


def _paragraph_text(p):
    return "".join(t.text or "" for t in p.iter(W("t")))


def fix_paragraph(p):
    """p is a <w:p> element."""
    if not ARABIC.search(_paragraph_text(p)):
        return False
    pPr = p.find(W("pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p.insert(0, pPr)
    bidi = _insert(pPr, "bidi")
    bidi.attrib.pop(W("val"), None)
    # forced left/right alignment flips meaning in an RTL paragraph → let it fall back to the start (right)
    jc = pPr.find(W("jc"))
    if jc is not None and jc.get(W("val")) in ("left", "right", "start", "end"):
        pPr.remove(jc)
    for r in p.iter(W("r")):
        fix_run(r)
    return True


def fix_run(r):
    text = "".join(t.text or "" for t in r.iter(W("t")))
    rPr = r.find(W("rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        r.insert(0, rPr)
    # Arabic is a "complex script": Word gives it its own font and size (szCs) — make them match the Latin ones
    sz = rPr.find(W("sz"))
    if sz is not None:
        _after(sz, "szCs").set(W("val"), sz.get(W("val")))
    fonts = rPr.find(W("rFonts"))
    if fonts is not None and fonts.get(W("ascii")) and not fonts.get(W("cs")):
        fonts.set(W("cs"), fonts.get(W("ascii")))
    b = rPr.find(W("b"))
    if b is not None:
        _after(b, "bCs")
    if ARABIC.search(text):
        _insert(rPr, "rtl")


def fix_tables(root):
    for tblPr in root.iter(W("tblPr")):
        _insert(tblPr, "bidiVisual")                     # first column on the right


def fix_styles(doc):
    """default run size/font for complex script = the Latin one (Normal style and docDefaults)."""
    styles = doc.styles.element
    for rPr in styles.iter(W("rPr")):
        sz = rPr.find(W("sz"))
        if sz is not None and rPr.find(W("szCs")) is None:
            _after(sz, "szCs").set(W("val"), sz.get(W("val")))


def fix(path_in, path_out=None):
    doc = Document(path_in)
    roots = [doc.element.body]
    for s in doc.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer, s.even_page_header, s.even_page_footer):
            if part is not None and not part.is_linked_to_previous:
                roots.append(part._element)
        _insert(s._sectPr, "bidi", "sect_bidi")         # page-level RTL (columns, gutter)
    n = 0
    for root in roots:
        for p in root.iter(W("p")):
            n += fix_paragraph(p)
        fix_tables(root)
    fix_styles(doc)
    zoom = doc.settings.element.find(W("zoom"))           # python-docx's template omits a required attribute
    if zoom is not None and zoom.get(W("percent")) is None:
        zoom.set(W("percent"), "100")
    out = Path(path_out) if path_out else Path(path_in).with_name(Path(path_in).stem + "_fixed.docx")
    doc.save(out)
    return out, n


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out, n = fix(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"✅ {n} فقرة عربية انصلحت → {out}")
