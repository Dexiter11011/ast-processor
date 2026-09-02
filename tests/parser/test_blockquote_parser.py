"""Blockquote parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_blockquote_parser():
    source = "> Quote line one.\n>\n> Quote line two."
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 1
    quote = doc.children[0]
    assert quote.type == "blockquote"
    assert len(quote.children) == 2
    assert quote.children[0].children[0].value == "Quote line one."
    assert quote.children[1].children[0].value == "Quote line two."
