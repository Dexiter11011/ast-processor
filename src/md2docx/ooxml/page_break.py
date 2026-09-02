"""OOXML page break builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.xml_builder import w_attr, w_tag


def build_page_break_paragraph() -> etree._Element:
    """Build a paragraph containing w:br w:type='page'."""
    p = build_paragraph([])
    r = etree.SubElement(p, w_tag("r"))
    br = etree.SubElement(r, w_tag("br"))
    br.set(w_attr("type"), "page")
    return p
