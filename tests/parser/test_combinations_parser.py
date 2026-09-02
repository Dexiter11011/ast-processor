"""Nested inline combination parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_bold_with_nested_italic():
    doc = MarkdownParser().parse("This is **bold and *italic***.")
    p = doc.children[0]
    assert len(p.children) == 3
    assert p.children[0].type == "text"
    assert p.children[0].value == "This is "
    strong = p.children[1]
    assert strong.type == "strong"
    assert len(strong.children) == 2
    assert strong.children[0].type == "text"
    assert strong.children[0].value == "bold and "
    emphasis = strong.children[1]
    assert emphasis.type == "emphasis"
    assert emphasis.children[0].value == "italic"
    assert p.children[2].type == "text"
    assert p.children[2].value == "."
