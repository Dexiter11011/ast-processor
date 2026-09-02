"""Ordered list parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_ordered_list_parser():
    doc = MarkdownParser().parse("1. First\n2. Second\n3. Third")
    assert len(doc.children) == 1
    lst = doc.children[0]
    assert lst.type == "list"
    assert lst.ordered is True
    assert len(lst.items) == 3
    assert lst.items[0].children[0].children[0].value == "First"
