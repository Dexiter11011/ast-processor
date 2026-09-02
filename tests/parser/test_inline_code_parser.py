"""Inline code parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_inline_code_parser():
    doc = MarkdownParser().parse("Run `npm install`.")
    p = doc.children[0]
    assert len(p.children) == 3
    assert p.children[0].type == "text"
    assert p.children[0].value == "Run "
    assert p.children[1].type == "inline_code"
    assert p.children[1].value == "npm install"
    assert p.children[2].type == "text"
    assert p.children[2].value == "."
