"""Unit tests for TemplateComposer."""

from __future__ import annotations

from lxml import etree

import pytest

from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import serialize, w_tag
from md2docx.templates.composer import TemplateComposer
from md2docx.templates.context import DocumentContext
from md2docx.templates.errors import TemplateInsertionError, TemplatePlaceholderError
from md2docx.templates.insertion import CONTENT_PLACEHOLDER


def _document_xml(*paragraph_texts: str) -> bytes:
    body = etree.Element(w_tag("body"), nsmap={"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"})
    for text in paragraph_texts:
        body.append(api.paragraph([api.run(text)], style_id="Normal"))
    sect_pr = etree.SubElement(body, w_tag("sectPr"))
    root = etree.Element(
        w_tag("document"),
        nsmap={
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        },
    )
    root.append(body)
    return serialize(root)


def test_compose_replaces_scalars_and_inserts_content():
    document_xml = _document_xml("Before", "{{title}}", CONTENT_PLACEHOLDER, "After")
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    context = DocumentContext(title="Project Documentation")
    result = TemplateComposer.compose_document(document_xml, fragment, context)
    text = result.decode("utf-8")
    assert "Project Documentation" in text
    assert "Body" in text
    assert "Before" in text
    assert "After" in text
    assert CONTENT_PLACEHOLDER not in text
    assert "{{title}}" not in text


def test_compose_missing_scalar_value_raises():
    document_xml = _document_xml("{{title}}", CONTENT_PLACEHOLDER)
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    with pytest.raises(TemplatePlaceholderError, match='missing value for template placeholder "{{title}}"'):
        TemplateComposer.compose_document(document_xml, fragment, DocumentContext())


def test_compose_unknown_placeholder_raises():
    document_xml = _document_xml("{{foo}}", CONTENT_PLACEHOLDER)
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    context = DocumentContext(title="T")
    with pytest.raises(TemplatePlaceholderError, match='unknown template placeholder "{{foo}}"'):
        TemplateComposer.compose_document(document_xml, fragment, context)


def test_compose_duplicate_content_raises():
    document_xml = _document_xml(CONTENT_PLACEHOLDER, "Middle", CONTENT_PLACEHOLDER)
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    with pytest.raises(TemplateInsertionError, match="multiple"):
        TemplateComposer.compose_document(document_xml, fragment, DocumentContext())


def test_compose_duplicate_scalar_uses_same_value():
    document_xml = _document_xml("{{title}}", CONTENT_PLACEHOLDER, "{{title}}")
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    context = DocumentContext(title="Same Title")
    result = TemplateComposer.compose_document(document_xml, fragment, context)
    assert result.decode("utf-8").count("Same Title") == 2


def test_compose_inline_scalar_raises():
    document_xml = _document_xml("Project: {{title}}", CONTENT_PLACEHOLDER)
    fragment = [api.paragraph([api.run("Body")], style_id="Normal")]
    context = DocumentContext(title="T")
    with pytest.raises(TemplatePlaceholderError, match="inline template placeholders are not supported"):
        TemplateComposer.compose_document(document_xml, fragment, context)
