"""OOXML horizontal rule builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import w_attr, w_element, w_tag


def build_horizontal_rule() -> etree._Element:
    """Build a paragraph with bottom border representing a horizontal rule."""
    p = w_element("p")
    p_pr = etree.SubElement(p, w_tag("pPr"))
    p_bdr = etree.SubElement(p_pr, w_tag("pBdr"))
    bottom = etree.SubElement(p_bdr, w_tag("bottom"))
    bottom.set(w_attr("val"), "single")
    bottom.set(w_attr("sz"), "6")
    bottom.set(w_attr("space"), "1")
    bottom.set(w_attr("color"), "auto")
    etree.SubElement(p, w_tag("r"))
    return p
