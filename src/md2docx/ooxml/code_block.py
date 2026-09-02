"""OOXML code block builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.style_ids import CODE_BLOCK
from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import w_tag

CODE_BLOCK_STYLE = CODE_BLOCK


def build_code_block_paragraph(value: str, *, style_id: str | None = None) -> etree._Element:
    """Build a code block paragraph; monospace comes from the paragraph style."""
    lines = value.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    p = build_paragraph([], style_id=style_id or CODE_BLOCK)
    r = etree.SubElement(p, w_tag("r"))

    if not lines:
        r.append(build_text(""))
        return p

    for index, line in enumerate(lines):
        if index > 0:
            etree.SubElement(r, w_tag("br"))
        r.append(build_text(line))
    return p
