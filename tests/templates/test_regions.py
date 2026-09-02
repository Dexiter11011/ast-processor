"""Unit tests for template navigation regions."""

from __future__ import annotations

import pytest
from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag
from md2docx.processor.context import ProcessingContext
from md2docx.templates.composer import TemplateComposer
from md2docx.templates.context import DocumentContext
from md2docx.templates.errors import TemplateInsertionError, TemplatePlaceholderError
from md2docx.templates.insertion import CONTENT_PLACEHOLDER, find_insertion_point, paragraph_text
from md2docx.templates.placeholder_scan import scan_body_placeholders
from md2docx.templates.placeholders import PlaceholderKind


def _document_xml(*paragraph_texts: str) -> bytes:
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    for text in paragraph_texts:
        body.append(api.paragraph([api.run(text)], style_id="Normal"))
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    return serialize(root)


def test_scan_recognizes_navigation_regions():
    document_xml = _document_xml("{{toc}}", "{{list_of_figures}}", CONTENT_PLACEHOLDER)
    placeholders = scan_body_placeholders(document_xml)
    names = [item.name for item in placeholders]
    kinds = {item.name: item.kind for item in placeholders}
    assert names == ["toc", "list_of_figures", "content"]
    assert kinds["toc"] is PlaceholderKind.NAVIGATION
    assert kinds["content"] is PlaceholderKind.CONTENT


def test_unknown_navigation_region_raises():
    document_xml = _document_xml("{{table_of_contents}}", CONTENT_PLACEHOLDER)
    with pytest.raises(TemplatePlaceholderError, match='unknown template placeholder "{{table_of_contents}}"'):
        scan_body_placeholders(document_xml)


def test_find_insertion_point_accepts_whitespace_in_content():
    document_xml = _document_xml("Before", "{{ content }}", "After")
    point = find_insertion_point(document_xml)
    assert point.paragraph_index == 1
    assert point.name == "content"


def test_compose_inserts_navigation_regions_in_template_order():
    document_xml = _document_xml(
        "Heading",
        "{{toc}}",
        "{{list_of_figures}}",
        CONTENT_PLACEHOLDER,
        "Footer",
    )
    content = [api.paragraph([api.run("Generated body")], style_id="Normal")]
    context = ProcessingContext.create_for_template()
    result = TemplateComposer.compose_document(
        document_xml,
        content,
        DocumentContext(),
        processing_context=context,
    )
    root = etree.fromstring(result)
    texts = [
        paragraph_text(node)
        for node in root.findall(f".//{w_tag('body')}/{w_tag('p')}")
    ]
    assert texts[0] == "Heading"
    assert texts[-1] == "Footer"
    assert "Generated body" in texts
    assert "{{toc}}" not in result.decode("utf-8")
    instr = [
        (node.text or "").strip()
        for node in root.findall(f".//{w_tag('instrText')}")
    ]
    assert any('TOC \\o "1-3"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)


def test_compose_content_before_navigation_when_template_orders_that_way():
    document_xml = _document_xml(
        CONTENT_PLACEHOLDER,
        "Appendix",
        "{{toc}}",
    )
    content = [api.paragraph([api.run("Main body")], style_id="Normal")]
    context = ProcessingContext.create_for_template()
    result = TemplateComposer.compose_document(
        document_xml,
        content,
        DocumentContext(),
        processing_context=context,
    )
    root = etree.fromstring(result)
    texts = [
        paragraph_text(node)
        for node in root.findall(f".//{w_tag('body')}/{w_tag('p')}")
    ]
    assert texts.index("Main body") < texts.index("Appendix")
    assert any('TOC \\o "1-3"' in (node.text or "") for node in root.findall(f".//{w_tag('instrText')}"))


def test_compose_duplicate_navigation_regions_allowed():
    document_xml = _document_xml("{{toc}}", CONTENT_PLACEHOLDER, "{{toc}}")
    content = [api.paragraph([api.run("Body")], style_id="Normal")]
    context = ProcessingContext.create_for_template()
    result = TemplateComposer.compose_document(
        document_xml,
        content,
        DocumentContext(),
        processing_context=context,
    )
    root = etree.fromstring(result)
    toc_fields = [
        (node.text or "")
        for node in root.findall(f".//{w_tag('instrText')}")
        if 'TOC \\o "1-3"' in (node.text or "")
    ]
    assert len(toc_fields) == 2


def test_compose_navigation_without_processing_context_raises():
    document_xml = _document_xml("{{toc}}", CONTENT_PLACEHOLDER)
    content = [api.paragraph([api.run("Body")], style_id="Normal")]
    with pytest.raises(TemplateInsertionError, match="navigation regions require a processing context"):
        TemplateComposer.compose_document(document_xml, content, DocumentContext())
