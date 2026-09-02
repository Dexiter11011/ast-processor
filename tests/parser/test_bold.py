"""Bold markdown parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_bold_parser():
    doc = MarkdownParser().parse("Hello **world**")
    p = doc.children[0]
    assert len(p.children) == 2
    assert p.children[0].type == "text"
    assert p.children[0].value == "Hello "
    assert p.children[1].type == "strong"
    assert p.children[1].children[0].value == "world"
