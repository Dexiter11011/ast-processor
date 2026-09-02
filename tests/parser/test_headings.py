"""Headings parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_headings_parser():
    source = "# Heading 1\n\n## Heading 2\n\n### Heading 3"
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 3
    assert doc.children[0].type == "heading"
    assert doc.children[0].level == 1
    assert doc.children[0].children[0].value == "Heading 1"
    assert doc.children[1].level == 2
    assert doc.children[2].level == 3
