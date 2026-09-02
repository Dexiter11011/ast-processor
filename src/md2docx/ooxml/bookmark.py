"""OOXML bookmark builders."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, w_attr, w_tag


def build_bookmark_start(name: str, bookmark_id: int) -> etree._Element:
    start = etree.Element(w_tag("bookmarkStart"), nsmap={"w": W_NS})
    start.set(w_attr("id"), str(bookmark_id))
    start.set(w_attr("name"), name)
    return start


def build_bookmark_end(bookmark_id: int) -> etree._Element:
    end = etree.Element(w_tag("bookmarkEnd"), nsmap={"w": W_NS})
    end.set(w_attr("id"), str(bookmark_id))
    return end


def wrap_paragraph_with_bookmark(
    paragraph: etree._Element,
    *,
    name: str,
    bookmark_id: int,
) -> etree._Element:
    """Insert bookmarkStart before first content and bookmarkEnd after last."""
    children = list(paragraph)
    p_pr = paragraph.find(w_tag("pPr"))
    insert_at = 1 if p_pr is not None else 0
    paragraph.insert(insert_at, build_bookmark_start(name, bookmark_id))
    paragraph.append(build_bookmark_end(bookmark_id))
    return paragraph
