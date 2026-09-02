"""GFM parser unit tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_task_list_checked_metadata():
    doc = MarkdownParser().parse("- [ ] Todo\n- [x] Done\n- Plain")
    items = doc.children[0].items
    assert items[0].checked is False
    assert items[0].children[0].children[0].value == "Todo"
    assert items[1].checked is True
    assert items[2].checked is None


def test_strikethrough_ast_node():
    doc = MarkdownParser().parse("~~deleted~~")
    child = doc.children[0].children[0]
    assert child.type == "strikethrough"
    assert child.children[0].value == "deleted"


def test_hard_break_ast_node():
    doc = MarkdownParser().parse("First  \nSecond")
    nodes = doc.children[0].children
    assert nodes[0].type == "text"
    assert nodes[1].type == "line_break"
    assert nodes[2].type == "text"


def test_autolink_produces_link_node():
    doc = MarkdownParser().parse("<https://example.com>")
    link = doc.children[0].children[0]
    assert link.type == "link"
    assert link.url == "https://example.com"
