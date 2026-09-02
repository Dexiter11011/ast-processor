"""WordprocessingML footnote builders."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, ns_tag, serialize, sub_element, w_attr, w_tag


def build_footnote_reference_run(footnote_id: int) -> etree._Element:
    run = etree.Element(w_tag("r"), nsmap={"w": W_NS})
    r_pr = sub_element(run, "rPr")
    r_style = sub_element(r_pr, "rStyle")
    r_style.set(w_attr("val"), "FootnoteReference")
    ref = sub_element(run, "footnoteReference")
    ref.set(w_attr("id"), str(footnote_id))
    return run


def _separator_paragraph() -> etree._Element:
    paragraph = etree.Element(w_tag("p"), nsmap={"w": W_NS})
    run = sub_element(paragraph, "r")
    separator = sub_element(run, "separator")
    return paragraph


def _continuation_separator_paragraph() -> etree._Element:
    paragraph = etree.Element(w_tag("p"), nsmap={"w": W_NS})
    run = sub_element(paragraph, "r")
    separator = sub_element(run, "continuationSeparator")
    return paragraph


def build_footnotes_xml(bodies: dict[int, list[etree._Element]]) -> bytes:
    root = etree.Element(w_tag("footnotes"), nsmap={"w": W_NS})

    sep = sub_element(root, "footnote")
    sep.set(w_attr("type"), "separator")
    sep.set(w_attr("id"), "-1")
    sep.append(_separator_paragraph())

    cont = sub_element(root, "footnote")
    cont.set(w_attr("type"), "continuationSeparator")
    cont.set(w_attr("id"), "0")
    cont.append(_continuation_separator_paragraph())

    for footnote_id in sorted(bodies):
        footnote = sub_element(root, "footnote")
        footnote.set(w_attr("id"), str(footnote_id))
        for paragraph in bodies[footnote_id]:
            footnote.append(paragraph)

    return serialize(root)
