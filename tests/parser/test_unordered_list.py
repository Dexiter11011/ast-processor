"""Unordered list parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_unordered_list_parser():
    doc = MarkdownParser().parse("- One\n- Two\n- Three")
    assert len(doc.children) == 1
    lst = doc.children[0]
    assert lst.type == "list"
    assert lst.ordered is False
    assert len(lst.items) == 3
    assert lst.items[0].children[0].children[0].value == "One"
