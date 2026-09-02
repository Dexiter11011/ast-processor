"""Parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_empty_markdown_returns_empty_document():
    doc = MarkdownParser().parse("")
    assert doc.type == "document"
    assert doc.children == []


def test_whitespace_only_returns_empty_document():
    doc = MarkdownParser().parse("   \n\n  \n")
    assert doc.children == []


def test_non_empty_parses_paragraph():
    doc = MarkdownParser().parse("Hello world")
    assert len(doc.children) == 1
    assert doc.children[0].type == "paragraph"
    assert doc.children[0].children[0].type == "text"
    assert doc.children[0].children[0].value == "Hello world"
