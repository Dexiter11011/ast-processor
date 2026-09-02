"""Template insertion point tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag
from md2docx.templates.errors import TemplateInsertionError, TemplatePlaceholderError
from md2docx.templates.insertion import CONTENT_PLACEHOLDER, find_insertion_point, insert_fragment, paragraph_text


def _document_xml(*paragraph_texts: str) -> bytes:
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    for text in paragraph_texts:
        body.append(api.paragraph([api.run(text)], style_id="Normal"))
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    return serialize(root)


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "templates"


def test_find_placeholder_in_minimal_template(templates_dir: Path):
    from tests.helpers import read_docx_part

    xml = read_docx_part(templates_dir / "minimal.docx", "word/document.xml")
    point = find_insertion_point(xml)
    assert point.paragraph_index == 1


def test_missing_placeholder_raises_error():
    with pytest.raises(TemplateInsertionError, match="was not found"):
        find_insertion_point(_document_xml("Introduction", "Signature"))


def test_duplicate_placeholder_raises_error():
    with pytest.raises(TemplateInsertionError, match="multiple"):
        find_insertion_point(
            _document_xml("Intro", CONTENT_PLACEHOLDER, "Middle", CONTENT_PLACEHOLDER)
        )


def test_inline_placeholder_raises_error():
    with pytest.raises(TemplatePlaceholderError, match="inline template placeholders are not supported"):
        find_insertion_point(_document_xml(f"Intro {CONTENT_PLACEHOLDER}"))


def test_find_insertion_point_accepts_spaced_content_placeholder():
    point = find_insertion_point(_document_xml("Before", "{{ content }}", "After"))
    assert point.paragraph_index == 1


def test_insert_fragment_replaces_placeholder():
    document = _document_xml("Before", CONTENT_PLACEHOLDER, "After")
    insertion = find_insertion_point(document)
    fragment = [api.paragraph([api.run("Generated")], style_id="Normal")]
    merged = insert_fragment(document, insertion, fragment)
    root = etree.fromstring(merged)
    texts = [
        paragraph_text(node)
        for node in root.findall(f".//{w_tag('body')}/{w_tag('p')}")
    ]
    assert texts == ["Before", "Generated", "After"]


def test_paragraph_text_concatenates_split_runs():
    paragraph = api.paragraph([api.run("{{"), api.run("content"), api.run("}}")], style_id="Normal")
    assert paragraph_text(paragraph) == CONTENT_PLACEHOLDER
