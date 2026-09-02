"""Render semantic dynamic fields to WordprocessingML."""

from __future__ import annotations

from lxml import etree

from md2docx.fields.kinds import FieldKind
from md2docx.fields.model import DynamicField
from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import W_NS, w_attr, w_tag

_SIMPLE_INSTRUCTIONS = {
    FieldKind.PAGE: " PAGE ",
    FieldKind.NUMPAGES: " NUMPAGES ",
    FieldKind.DATE: " DATE ",
    FieldKind.AUTHOR: " AUTHOR ",
    FieldKind.TITLE: " TITLE ",
}

_SIMPLE_CACHED_RESULTS = {
    FieldKind.PAGE: "1",
    FieldKind.NUMPAGES: "1",
    FieldKind.DATE: "01/01/2026",
    FieldKind.AUTHOR: "Author",
    FieldKind.TITLE: "Title",
}


def _field_run(char_type: str) -> etree._Element:
    run = etree.Element(w_tag("r"), nsmap={"w": W_NS})
    fld_char = etree.SubElement(run, w_tag("fldChar"))
    fld_char.set(w_attr("fldCharType"), char_type)
    return run


def _instr_run(instruction: str) -> etree._Element:
    run = etree.Element(w_tag("r"), nsmap={"w": W_NS})
    instr = etree.SubElement(run, w_tag("instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = instruction
    return run


def _result_run(text: str) -> etree._Element:
    run = etree.Element(w_tag("r"), nsmap={"w": W_NS})
    run.append(build_text(text))
    return run


def build_fld_simple(instruction: str, *, cached_result: str = "") -> etree._Element:
    """Build a w:fldSimple element with optional cached display text."""
    fld = etree.Element(w_tag("fldSimple"), nsmap={"w": W_NS})
    fld.set(w_attr("instr"), instruction)
    if cached_result:
        fld.append(_result_run(cached_result))
    return fld


def build_complex_field(
    instruction: str,
    *,
    cached_result: str = "",
) -> list[etree._Element]:
    """Build complex field runs: begin, instrText, separate, [result], end."""
    runs: list[etree._Element] = [
        _field_run("begin"),
        _instr_run(instruction),
        _field_run("separate"),
    ]
    if cached_result:
        runs.append(_result_run(cached_result))
    runs.append(_field_run("end"))
    return runs


def build_toc_field(*, min_level: int = 1, max_level: int = 3) -> etree._Element:
    """Build a w:p containing a Word TOC complex field."""
    from md2docx.ooxml.paragraph import build_paragraph

    instruction = f' TOC \\o "{min_level}-{max_level}" \\h \\z \\u '
    runs = build_complex_field(instruction)
    return build_paragraph(runs)


def build_lof_field() -> etree._Element:
    """Build a w:p containing a Word List of Figures field (TOC \\c "Figure")."""
    from md2docx.ooxml.paragraph import build_paragraph

    instruction = ' TOC \\h \\z \\c "Figure" '
    runs = build_complex_field(instruction)
    return build_paragraph(runs)


def build_lot_field() -> etree._Element:
    """Build a w:p containing a Word List of Tables field (TOC \\c "Table")."""
    from md2docx.ooxml.paragraph import build_paragraph

    instruction = ' TOC \\h \\z \\c "Table" '
    runs = build_complex_field(instruction)
    return build_paragraph(runs)


class FieldRenderer:
    """Convert DynamicField objects into OOXML paragraph children."""

    @staticmethod
    def render(
        field: DynamicField,
        *,
        title_display: str | None = None,
        author_display: str | None = None,
    ) -> list[etree._Element]:
        if field.kind in _SIMPLE_INSTRUCTIONS:
            instruction = _SIMPLE_INSTRUCTIONS[field.kind]
            cached = _SIMPLE_CACHED_RESULTS[field.kind]
            if field.kind is FieldKind.TITLE and title_display:
                cached = title_display
            elif field.kind is FieldKind.AUTHOR and author_display:
                cached = author_display
            return [build_fld_simple(instruction, cached_result=cached)]

        if field.kind is FieldKind.REF:
            target = field.target or ""
            switches = " ".join(field.switches) if field.switches else "\\h"
            instruction = f" REF {target} {switches} "
            return build_complex_field(instruction, cached_result="Reference")

        if field.kind is FieldKind.SEQ:
            target = field.target or ""
            switches = " ".join(field.switches)
            instruction = f" SEQ {target} {switches} ".strip() + " "
            return build_complex_field(instruction, cached_result="1")

        raise ValueError(f"unsupported dynamic field kind: {field.kind}")
