"""Unit tests for scalar placeholder replacement."""

from __future__ import annotations

import pytest
from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import W_NS, serialize, w_tag
from md2docx.templates.errors import TemplatePlaceholderError
from md2docx.templates.placeholders import PlaceholderKind, TemplatePlaceholder
from md2docx.templates.scalar_replace import replace_scalar_placeholder, validate_scalar_value


def _paragraph_xml(text: str, *, style_id: str = "Normal") -> etree._Element:
    return api.paragraph([api.run(text)], style_id=style_id)


def test_replace_scalar_preserves_paragraph_style():
    paragraph = _paragraph_xml("{{title}}", style_id="Heading1")
    placeholder = TemplatePlaceholder(
        name="title",
        kind=PlaceholderKind.SCALAR,
        paragraph_index=0,
        raw="{{title}}",
    )
    replace_scalar_placeholder(paragraph, placeholder, "Project Documentation")
    p_pr = paragraph.find(w_tag("pPr"))
    assert p_pr is not None
    style = p_pr.find(w_tag("pStyle"))
    assert style is not None
    assert style.get(w_tag("val")) == "Heading1"
    text_nodes = list(paragraph.iter(w_tag("t")))
    assert len(text_nodes) == 1
    assert text_nodes[0].text == "Project Documentation"


def test_replace_scalar_xml_escapes_special_characters():
    paragraph = _paragraph_xml("{{title}}")
    placeholder = TemplatePlaceholder(
        name="title",
        kind=PlaceholderKind.SCALAR,
        paragraph_index=0,
        raw="{{title}}",
    )
    replace_scalar_placeholder(paragraph, placeholder, "A & B <Draft>")
    xml = serialize(paragraph)
    assert "A &amp; B &lt;Draft&gt;" in xml.decode("utf-8")


def test_replace_scalar_rejects_newlines():
    with pytest.raises(TemplatePlaceholderError, match="must not contain newlines"):
        validate_scalar_value("title", "Line 1\nLine 2")
