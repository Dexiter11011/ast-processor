"""Multiple paragraphs parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_multiple_paragraphs():
    source = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 3
    assert all(c.type == "paragraph" for c in doc.children)
    assert doc.children[0].children[0].value == "First paragraph."
    assert doc.children[1].children[0].value == "Second paragraph."
    assert doc.children[2].children[0].value == "Third paragraph."
