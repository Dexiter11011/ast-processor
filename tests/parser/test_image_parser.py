"""Image parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_image_block_parser():
    doc = MarkdownParser().parse("![Logo](logo.png)")
    assert len(doc.children) == 1
    image = doc.children[0]
    assert image.type == "image"
    assert image.src == "logo.png"
    assert image.alt == "Logo"
