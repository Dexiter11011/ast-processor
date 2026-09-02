"""Horizontal rule parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_horizontal_rule_parser():
    doc = MarkdownParser().parse("Before\n\n---\n\nAfter")
    assert len(doc.children) == 3
    assert doc.children[0].type == "paragraph"
    assert doc.children[1].type == "horizontal_rule"
    assert doc.children[2].type == "paragraph"
