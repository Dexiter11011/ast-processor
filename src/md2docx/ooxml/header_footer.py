"""OOXML header and footer part builders."""

from __future__ import annotations

from copy import deepcopy

from lxml import etree

from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag


def build_header_part(paragraphs: list[etree._Element]) -> bytes:
    root = etree.Element(w_tag("hdr"), nsmap={"w": W_NS, "r": R_NS})
    for paragraph in paragraphs:
        root.append(deepcopy(paragraph))
    return serialize(root)


def build_footer_part(paragraphs: list[etree._Element]) -> bytes:
    root = etree.Element(w_tag("ftr"), nsmap={"w": W_NS, "r": R_NS})
    for paragraph in paragraphs:
        root.append(deepcopy(paragraph))
    return serialize(root)
