"""Link parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_link_parser():
    doc = MarkdownParser().parse("Visit [OpenAI](https://openai.com).")
    p = doc.children[0]
    assert len(p.children) == 3
    assert p.children[0].type == "text"
    assert p.children[0].value == "Visit "
    link = p.children[1]
    assert link.type == "link"
    assert link.url == "https://openai.com"
    assert link.children[0].value == "OpenAI"
    assert p.children[2].value == "."
