"""OOXML run builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import w_element, w_tag


def build_run(
    children: list[etree._Element] | None = None,
    *,
    bold: bool = False,
    italic: bool = False,
    font: str = "",
    r_style: str = "",
) -> etree._Element:
    r = w_element("r")
    if bold or italic or font or r_style:
        r_pr = etree.SubElement(r, w_tag("rPr"))
        if r_style:
            r_style_el = etree.SubElement(r_pr, w_tag("rStyle"))
            r_style_el.set(w_tag("val"), r_style)
        if italic:
            etree.SubElement(r_pr, w_tag("i"))
        if bold:
            etree.SubElement(r_pr, w_tag("b"))
        if font:
            fonts = etree.SubElement(r_pr, w_tag("rFonts"))
            fonts.set(w_tag("ascii"), font)
            fonts.set(w_tag("hAnsi"), font)
            fonts.set(w_tag("cs"), font)
    if children:
        for child in children:
            r.append(child)
    return r
