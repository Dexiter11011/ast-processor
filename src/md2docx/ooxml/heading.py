"""OOXML heading paragraph builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.paragraph import build_paragraph


def build_heading(runs: list[etree._Element], *, style_id: str) -> etree._Element:
    return build_paragraph(runs, style_id=style_id)
