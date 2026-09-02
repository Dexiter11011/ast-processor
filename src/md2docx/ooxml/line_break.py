"""OOXML line break builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import w_element, w_tag


def build_line_break_run() -> etree._Element:
    """Build a w:r containing w:br for a hard line break inside a paragraph."""
    run = w_element("r")
    etree.SubElement(run, w_tag("br"))
    return run
