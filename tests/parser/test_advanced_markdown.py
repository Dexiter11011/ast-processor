"""Advanced Markdown parser tests (footnotes, definition lists, safe HTML)."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.parser.errors import FootnoteParseError, HtmlParseError
from md2docx.parser.footnote_transform import apply_footnote_transform
from md2docx.parser.markdown_parser import MarkdownParser


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "markdown" / "advanced"


def test_footnote_reference_and_definition():
    doc = apply_footnote_transform(
        MarkdownParser().parse("Body[^note].\n\n[^note]: Footnote text.")
    )
    assert doc.children[0].children[1].type == "footnote_reference"
    assert doc.children[0].children[1].label == "note"
    assert len(doc.footnotes) == 1
    assert doc.footnotes[0].label == "note"
    assert doc.footnotes[0].children[0].children[0].value == "Footnote text."


def test_undefined_footnote_raises():
    with pytest.raises(FootnoteParseError, match="undefined footnote"):
        apply_footnote_transform(MarkdownParser().parse("Missing[^missing]."))


def test_duplicate_footnote_definition_raises():
    source = "Text[^1].\n\n[^1]: first\n\n[^1]: second"
    with pytest.raises(FootnoteParseError, match="duplicate footnote definition"):
        apply_footnote_transform(MarkdownParser().parse(source), source=source)


def test_definition_list_ast():
    doc = MarkdownParser().parse("Apple\n: A fruit\n")
    block = doc.children[0]
    assert block.type == "definition_list"
    assert block.items[0].term[0].value == "Apple"
    assert block.items[0].description[0].children[0].value == "A fruit"


def test_safe_html_maps_to_semantic_nodes():
    doc = MarkdownParser().parse("<strong>b</strong> <em>i</em> <del>d</del> <br> end")
    nodes = doc.children[0].children
    assert nodes[0].type == "strong"
    assert nodes[2].type == "emphasis"
    assert nodes[4].type == "strikethrough"
    assert nodes[6].type == "line_break"


def test_html_link_with_safe_scheme():
    doc = MarkdownParser().parse('<a href="https://example.com">Example</a>')
    link = doc.children[0].children[0]
    assert link.type == "link"
    assert link.url == "https://example.com"


def test_unsafe_html_scheme_raises():
    with pytest.raises(HtmlParseError, match="unsafe URL scheme"):
        MarkdownParser().parse('<a href="javascript:alert(1)">x</a>')


def test_blocked_html_element_raises():
    with pytest.raises(HtmlParseError, match="unsupported HTML element: script"):
        MarkdownParser().parse("<script>alert(1)</script>")


def test_block_html_raises():
    with pytest.raises(HtmlParseError, match="unsupported HTML element: div"):
        MarkdownParser().parse("<div>block</div>")


def test_advanced_fixture_parses():
    source = (FIXTURES / "footnotes-deflist-html.md").read_text(encoding="utf-8")
    doc = apply_footnote_transform(MarkdownParser().parse(source))
    assert any(child.type == "definition_list" for child in doc.children)
    assert doc.footnotes[0].label == "1"
