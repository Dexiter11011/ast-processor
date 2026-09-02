"""OOXML text builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import XML_NS, text_element, w_tag


def build_text(value: str) -> etree._Element:
    """Build a w:t element with safe text content and xml:space when needed."""
    t = text_element("t", value)
    if value.startswith(" ") or value.endswith(" "):
        t.set(f"{{{XML_NS}}}space", "preserve")
    return t
