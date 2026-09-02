"""Table directive parser tests."""

from md2docx.parser.table_directive import is_table_directive_text, parse_cell_align, parse_table_directive


def test_parse_table_directive():
    source = "<!-- table: borders=none -->\n| A | B |"
    assert parse_table_directive(source, 1) == {"borders": "none"}
    assert is_table_directive_text("<!-- table: borders=none -->")
    assert not is_table_directive_text("Not a directive")


def test_parse_cell_align():
    assert parse_cell_align({"style": "text-align:center"}) == "center"
    assert parse_cell_align({}) == ""
