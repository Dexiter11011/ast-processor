"""Run property helpers (internal OOXML detail)."""

from __future__ import annotations

from typing import Protocol

from lxml import etree

from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import w_tag


class _InlineFormattingLike(Protocol):
    bold: bool
    italic: bool
    code: bool
    strike: bool


def apply_run_property(run: etree._Element, property_tag: str) -> etree._Element:
    r_pr = run.find(w_tag("rPr"))
    if r_pr is None:
        r_pr = etree.SubElement(run, w_tag("rPr"))
        run.insert(0, r_pr)
    if r_pr.find(w_tag(property_tag)) is None:
        etree.SubElement(r_pr, w_tag(property_tag))
    return run


def apply_inline_formatting(
    run: etree._Element,
    formatting: _InlineFormattingLike,
    *,
    r_style: str = "",
) -> etree._Element:
    """Apply accumulated inline formatting state to an existing w:r."""
    if formatting.bold:
        apply_run_property(run, "b")
    if formatting.italic:
        apply_run_property(run, "i")
    if formatting.strike:
        apply_run_property(run, "strike")
    if r_style:
        r_pr = run.find(w_tag("rPr"))
        if r_pr is None:
            r_pr = etree.SubElement(run, w_tag("rPr"))
            run.insert(0, r_pr)
        style_el = r_pr.find(w_tag("rStyle"))
        if style_el is None:
            style_el = etree.SubElement(r_pr, w_tag("rStyle"))
        style_el.set(w_tag("val"), r_style)
    return run


def run_from_formatting(
    text: str,
    formatting: _InlineFormattingLike,
    *,
    r_style: str = "",
) -> etree._Element:
    """Build a w:r from text and inline formatting state."""
    from md2docx.ooxml.run import build_run

    run = build_run(
        [build_text(text)],
        bold=formatting.bold,
        italic=formatting.italic,
        r_style=r_style,
    )
    if formatting.strike:
        apply_run_property(run, "strike")
    return run
