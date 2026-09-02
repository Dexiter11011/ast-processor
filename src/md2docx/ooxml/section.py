"""OOXML section properties builder."""

from __future__ import annotations

from lxml import etree

from md2docx.sections.definition import Orientation, PageLayout
from md2docx.ooxml.xml_builder import R_NS, W_NS, w_attr, w_tag


def build_sect_pr(
    layout: PageLayout,
    *,
    header_rel_id: str | None = None,
    footer_rel_id: str | None = None,
) -> etree._Element:
    """Build w:sectPr for a section."""
    sect_pr = etree.Element(w_tag("sectPr"), nsmap={"w": W_NS, "r": R_NS})

    pg_sz = etree.SubElement(sect_pr, w_tag("pgSz"))
    width, height = layout.effective_size()
    pg_sz.set(w_attr("w"), str(width))
    pg_sz.set(w_attr("h"), str(height))
    if layout.orientation == Orientation.LANDSCAPE:
        pg_sz.set(w_attr("orient"), "landscape")

    if layout.margins is not None:
        pg_mar = etree.SubElement(sect_pr, w_tag("pgMar"))
        m = layout.margins
        pg_mar.set(w_attr("top"), str(m.top))
        pg_mar.set(w_attr("right"), str(m.right))
        pg_mar.set(w_attr("bottom"), str(m.bottom))
        pg_mar.set(w_attr("left"), str(m.left))
        pg_mar.set(w_attr("header"), str(m.header))
        pg_mar.set(w_attr("footer"), str(m.footer))

    if header_rel_id:
        header_ref = etree.SubElement(sect_pr, w_tag("headerReference"))
        header_ref.set(w_attr("type"), "default")
        header_ref.set(f"{{{R_NS}}}id", header_rel_id)

    if footer_rel_id:
        footer_ref = etree.SubElement(sect_pr, w_tag("footerReference"))
        footer_ref.set(w_attr("type"), "default")
        footer_ref.set(f"{{{R_NS}}}id", footer_rel_id)

    return sect_pr


def attach_sect_pr_to_paragraph(paragraph: etree._Element, sect_pr: etree._Element) -> None:
    """Attach inline w:sectPr to a paragraph's w:pPr (section boundary)."""
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        p_pr = etree.SubElement(paragraph, w_tag("pPr"))
        paragraph.insert(0, p_pr)
    p_pr.append(sect_pr)
