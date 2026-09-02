"""OOXML paragraph builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import w_attr, w_element, w_tag


def build_paragraph(
    children: list[etree._Element] | None = None,
    *,
    style_id: str | None = None,
    num_id: int | None = None,
    num_level: int = 0,
    indent_left_twips: int | None = None,
) -> etree._Element:
    p = w_element("p")
    if style_id is not None or num_id is not None or indent_left_twips is not None:
        p_pr = etree.SubElement(p, w_tag("pPr"))
        if style_id is not None:
            p_style = etree.SubElement(p_pr, w_tag("pStyle"))
            p_style.set(w_attr("val"), style_id)
        if indent_left_twips is not None:
            ind = etree.SubElement(p_pr, w_tag("ind"))
            ind.set(w_attr("left"), str(indent_left_twips))
        if num_id is not None:
            num_pr = etree.SubElement(p_pr, w_tag("numPr"))
            ilvl = etree.SubElement(num_pr, w_tag("ilvl"))
            ilvl.set(w_attr("val"), str(num_level))
            num_id_el = etree.SubElement(num_pr, w_tag("numId"))
            num_id_el.set(w_attr("val"), str(num_id))
    if children:
        for child in children:
            p.append(child)
    return p


def build_normal_separator_paragraph() -> etree._Element:
    """Plain Normal paragraph between block elements (lists, tables, …)."""
    return build_paragraph([], style_id="Normal")


def build_list_separator_paragraph() -> etree._Element:
    return build_normal_separator_paragraph()


def build_table_separator_paragraph() -> etree._Element:
    return build_normal_separator_paragraph()
