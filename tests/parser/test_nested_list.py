"""Nested list parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_nested_unordered_list_parser():
    source = "- One\n  - Nested A\n  - Nested B\n- Two"
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 1
    lst = doc.children[0]
    assert lst.type == "list"
    assert lst.ordered is False
    assert len(lst.items) == 2
    first = lst.items[0]
    assert len(first.children) == 2
    assert first.children[0].type == "paragraph"
    assert first.children[1].type == "list"
    nested = first.children[1]
    assert nested.ordered is False
    assert len(nested.items) == 2
    assert nested.items[0].children[0].children[0].value == "Nested A"
