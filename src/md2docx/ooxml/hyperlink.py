"""OOXML hyperlink builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import R_NS, W_NS, w_attr, w_tag

DEFAULT_LINK_COLOR = "0563C1"


def apply_link_style(
    run: etree._Element,
    *,
    color: str = DEFAULT_LINK_COLOR,
    underline: str = "single",
) -> etree._Element:
    r_pr = run.find(w_tag("rPr"))
    if r_pr is None:
        r_pr = etree.SubElement(run, w_tag("rPr"))
        run.insert(0, r_pr)
    if underline and r_pr.find(w_tag("u")) is None:
        u = etree.SubElement(r_pr, w_tag("u"))
        u.set(w_attr("val"), underline)
    if color and r_pr.find(w_tag("color")) is None:
        color_el = etree.SubElement(r_pr, w_tag("color"))
        color_el.set(w_attr("val"), color)
    return run


def build_hyperlink(
    runs: list[etree._Element],
    *,
    rel_id: str | None = None,
    anchor: str | None = None,
) -> etree._Element:
    if (rel_id is None) == (anchor is None):
        raise ValueError("build_hyperlink requires exactly one of rel_id or anchor")
    hyper = etree.Element(
        w_tag("hyperlink"),
        nsmap={"w": W_NS, "r": R_NS},
    )
    if rel_id is not None:
        hyper.set(w_attr("history"), "1")
        hyper.set(f"{{{R_NS}}}id", rel_id)
    else:
        hyper.set(w_attr("anchor"), anchor or "")
    for run in runs:
        hyper.append(run)
    return hyper
