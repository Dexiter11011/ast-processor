"""Scan template document.xml for placeholders."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import w_tag
from md2docx.templates.errors import TemplateInsertionError, TemplatePlaceholderError
from md2docx.templates.insertion import paragraph_text
from md2docx.templates.placeholder_parser import TemplatePlaceholderParser
from md2docx.templates.placeholders import TemplatePlaceholder, kind_for_name


def scan_body_placeholders(
    document_xml: bytes,
    *,
    extra_placeholders: dict[str, PlaceholderKind] | None = None,
) -> list[TemplatePlaceholder]:
    """Scan direct body paragraphs for standalone template placeholders."""
    root = etree.fromstring(document_xml)
    body = root.find(w_tag("body"))
    if body is None:
        raise TemplateInsertionError("template document.xml has no w:body")

    placeholders: list[TemplatePlaceholder] = []
    paragraph_index = 0
    for child in body:
        if etree.QName(child).localname != "p":
            continue
        text = paragraph_text(child)
        if not TemplatePlaceholderParser.looks_like_placeholder_paragraph(text):
            paragraph_index += 1
            continue

        name = TemplatePlaceholderParser.parse_standalone(text)
        if name is None:
            paragraph_index += 1
            continue

        kind = kind_for_name(name, extra=extra_placeholders)
        if kind is None:
            raise TemplatePlaceholderError(f'unknown template placeholder "{{{{{name}}}}}"')

        placeholders.append(
            TemplatePlaceholder(
                name=name,
                kind=kind,
                paragraph_index=paragraph_index,
                raw=text.strip(),
            )
        )
        paragraph_index += 1

    return placeholders
