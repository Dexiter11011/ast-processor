"""Cell marker parser tests."""

from md2docx.parser.cell_markers import parse_cell_content, parse_gost_cell_align, resolve_fill_color


def test_resolve_fill_color():
    assert resolve_fill_color("yellow") == "FFF2CC"
    assert resolve_fill_color("AABBCC") == "AABBCC"


def test_parse_gost_cell_align():
    assert parse_gost_cell_align(":center:") == ("center", "center")
    assert parse_gost_cell_align(":left") == ("left", "left")
    assert parse_gost_cell_align("right:") == ("right", "right")


def test_parse_cell_content_markers():
    parsed = parse_cell_content("{bg:yellow}{valign:center}:Centered:")
    assert parsed.bg == "FFF2CC"
    assert parsed.valign == "center"
    assert parsed.align == "center"
    assert parsed.text == "Centered"


def test_parse_cell_content_vmerge_marker():
    parsed = parse_cell_content("^^")
    assert parsed.vmerge_continue is True
