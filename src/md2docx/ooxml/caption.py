"""OOXML caption paragraph builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.bookmark import wrap_paragraph_with_bookmark
from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.run import build_run
from md2docx.ooxml.text import build_text


def build_caption_paragraph(
    *,
    label: str,
    seq_runs: list[etree._Element],
    separator: str,
    content_runs: list[etree._Element],
    style_id: str,
    bookmark_name: str,
    bookmark_id: int,
) -> etree._Element:
    """Build a captioned paragraph: label + SEQ + separator + content, with bookmark."""
    runs: list[etree._Element] = []
    if label:
        runs.append(build_run([build_text(label)]))
    runs.extend(seq_runs)
    if separator:
        runs.append(build_run([build_text(separator)]))
    runs.extend(content_runs)
    paragraph = build_paragraph(runs, style_id=style_id)
    return wrap_paragraph_with_bookmark(paragraph, name=bookmark_name, bookmark_id=bookmark_id)
