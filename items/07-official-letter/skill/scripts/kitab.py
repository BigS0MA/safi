#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""كتاب رسمي بالعربي → ملف Word (.docx) مزبوط من اليمين لليسار.

  python3 kitab.py letter.json [out.docx] [--font "Arial"]

letter.json:
  {"ref": "", "date": "4/11/2026",
   "to": "حضرة عميد كلية تكنولوجيا المعلومات المحترم",
   "subject": "طلب تأجيل امتحان",
   "body": ["فقرة 1", "فقرة 2"],
   "closing": "وتفضلوا بقبول فائق الاحترام والتقدير،",
   "name": "الاسم", "role": "الصفة أو الرقم الجامعي", "attachments": ["تقرير طبي"]}

Layout (common Arabic official letter): reference + date on the left, recipient on the right,
subject centred and bold, greeting, body, closing, name + role on the left, attachments.
Needs: pip install python-docx
"""
import json
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

W = lambda t: qn(f"w:{t}")
# in a right-to-left paragraph Word reads jc "left/right" as start/end of the line:
VISUAL = {"right": None, "left": "right", "center": "center", "justify": "both"}
PPR_AFTER_BIDI = {W(t) for t in ("adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
                                 "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl",
                                 "divId", "cnfStyle", "rPr", "sectPr", "pPrChange")}


def para(doc, text, font, size=14, bold=False, side="right", after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.35
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    for child in pPr:                                   # keep ECMA-376 order
        if child.tag in PPR_AFTER_BIDI:
            child.addprevious(bidi)
            break
    else:
        pPr.append(bidi)
    jc = VISUAL[side]
    if jc:
        el = OxmlElement("w:jc")
        el.set(W("val"), jc)
        pPr.append(el)
    r = p.add_run(text)
    r.font.name, r.font.size, r.bold = font, Pt(size), bold
    rPr = r._r.get_or_add_rPr()
    rPr.find(W("rFonts")).set(W("cs"), font)
    if bold:
        rPr.find(W("b")).addnext(OxmlElement("w:bCs"))
    szcs = OxmlElement("w:szCs")
    szcs.set(W("val"), str(size * 2))
    rPr.find(W("sz")).addnext(szcs)
    rtl = OxmlElement("w:rtl")
    rPr.append(rtl)
    return p


def build(spec, out, font="Arial"):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for side in ("left_margin", "right_margin"):
        setattr(sec, side, Cm(2.5))
    sec.top_margin = sec.bottom_margin = Cm(2.5)
    sbidi = OxmlElement("w:bidi")                       # page-level RTL, before rtlGutter/docGrid (ECMA-376 order)
    later = {W(t) for t in ("rtlGutter", "docGrid", "printerSettings", "sectPrChange")}
    nxt = next((c for c in sec._sectPr if c.tag in later), None)
    (nxt.addprevious(sbidi) if nxt is not None else sec._sectPr.append(sbidi))
    zoom = doc.settings.element.find(W("zoom"))
    if zoom is not None and zoom.get(W("percent")) is None:
        zoom.set(W("percent"), "100")
    para(doc, f'الرقم: {spec.get("ref") or "........"}', font, 12, side="left", after=0)
    para(doc, f'التاريخ: {spec.get("date") or "..../..../......"}', font, 12, side="left", after=18)
    para(doc, spec["to"], font, 15, bold=True, after=14)
    para(doc, f'الموضوع: {spec["subject"]}', font, 15, bold=True, side="center", after=14)
    para(doc, "تحية طيبة وبعد،", font, 14, after=10)
    for b in spec["body"]:
        para(doc, b, font, 14, side="justify", after=10)
    para(doc, spec.get("closing") or "وتفضلوا بقبول فائق الاحترام والتقدير،", font, 14, after=28)
    para(doc, spec["name"], font, 14, bold=True, side="left", after=0)
    if spec.get("role"):
        para(doc, spec["role"], font, 13, side="left", after=0)
    para(doc, "التوقيع: ................", font, 13, side="left", after=18)
    if spec.get("attachments"):
        para(doc, "المرفقات:", font, 13, bold=True, after=0)
        for a in spec["attachments"]:
            para(doc, f"- {a}", font, 13, after=0)
    doc.save(out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    font = "Arial"
    if "--font" in args:
        i = args.index("--font")
        font = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    out = args[1] if len(args) > 1 else str(Path(args[0]).with_suffix(".docx"))
    print("✅", build(spec, out, font))
