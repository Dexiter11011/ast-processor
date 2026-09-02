"""Detect and apply template region insertion points in template document.xml."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from lxml import etree

from md2docx.ooxml.xml_builder import w_tag
from md2docx.templates.errors import TemplateInsertionError
from md2docx.templates.placeholder_parser import TemplatePlaceholderParser


CONTENT_PLACEHOLDER = "{{content}}"


@dataclass(frozen=True)
class TemplateInsertionPoint:
    """Location of a standalone template region placeholder paragraph."""

    name: str
    paragraph_index: int


def paragraph_text(paragraph: etree._Element) -> str:
    """Concatenate all w:t text within a paragraph."""
    chunks: list[str] = []
    for node in paragraph.iter(w_tag("t")):
        if node.text:
            chunks.append(node.text)
    return "".join(chunks)


def find_insertion_point(document_xml: bytes) -> TemplateInsertionPoint:
    """Locate exactly one standalone {{content}} paragraph."""
    points = find_region_insertion_points(document_xml, {"content"})
    content_points = [point for point in points if point.name == "content"]
    if not content_points:
        raise TemplateInsertionError('template insertion point "{{content}}" was not found')
    if len(content_points) > 1:
        raise TemplateInsertionError("template contains multiple {{content}} insertion points")
    return content_points[0]


def find_region_insertion_points(
    document_xml: bytes,
    region_names: set[str],
) -> list[TemplateInsertionPoint]:
    """Locate standalone region placeholder paragraphs in document order."""
    root = etree.fromstring(document_xml)
    body = root.find(w_tag("body"))
    if body is None:
        raise TemplateInsertionError("template document.xml has no w:body")

    matches: list[TemplateInsertionPoint] = []
    index = 0
    for child in body:
        if etree.QName(child).localname != "p":
            continue
        text = paragraph_text(child)
        name = TemplatePlaceholderParser.parse_standalone(text)
        if name is not None and name in region_names:
            matches.append(TemplateInsertionPoint(name=name, paragraph_index=index))
        index += 1
    return matches


def insert_fragment(
    document_xml: bytes,
    insertion: TemplateInsertionPoint,
    fragment_children: list[etree._Element],
) -> bytes:
    """Replace the placeholder paragraph with generated body elements."""
    return insert_fragment_at_index(document_xml, insertion.paragraph_index, fragment_children)


def insert_fragment_at_index(
    document_xml: bytes,
    paragraph_index: int,
    fragment_children: list[etree._Element],
) -> bytes:
    """Replace a body paragraph at *paragraph_index* with generated body elements."""
    root = etree.fromstring(document_xml)
    body = root.find(w_tag("body"))
    if body is None:
        raise TemplateInsertionError("template document.xml has no w:body")

    paragraphs = [child for child in body if etree.QName(child).localname == "p"]
    if paragraph_index >= len(paragraphs):
        raise TemplateInsertionError("template insertion point paragraph index out of range")

    target = paragraphs[paragraph_index]
    parent = target.getparent()
    if parent is None:
        raise TemplateInsertionError("template insertion point has no parent")

    insert_at = parent.index(target)
    parent.remove(target)
    for offset, child in enumerate(fragment_children):
        parent.insert(insert_at + offset, deepcopy(child))

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def parse_document_body(document_xml: bytes) -> etree._Element:
    root = etree.fromstring(document_xml)
    body = root.find(w_tag("body"))
    if body is None:
        raise TemplateInsertionError("template document.xml has no w:body")
    return body


def max_bookmark_id(document_xml: bytes) -> int:
    """Return the highest bookmark id present in template document.xml."""
    root = etree.fromstring(document_xml)
    max_id = -1
    for node in root.iter(w_tag("bookmarkStart")):
        raw = node.get(w_tag("id"))
        if raw is not None and raw.isdigit():
            max_id = max(max_id, int(raw))
    return max_id
