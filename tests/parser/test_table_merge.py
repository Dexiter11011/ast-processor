"""Table merge parser tests."""

from md2docx.ast.types import Paragraph, TableCell, TableRow, Text
from md2docx.parser.markdown_parser import MarkdownParser
from md2docx.ast.table_merge import apply_horizontal_merge, apply_vertical_merge, table_logical_column_count


def _cell(text: str) -> TableCell:
    return TableCell(children=[Paragraph(children=[Text(value=text)])])


def test_apply_horizontal_merge():
    cells = [_cell("Europe"), TableCell(), _cell("—")]
    merged = apply_horizontal_merge(cells)
    assert merged[0].colspan == 2
    assert merged[1].merged is True
    assert merged[2].children[0].children[0].value == "—"


def test_apply_vertical_merge():
    rows = [
        TableRow(cells=[_cell("Fruits"), _cell("Apple"), _cell("5")]),
        TableRow(cells=[TableCell(vmerge_continue=True), _cell("Banana"), _cell("3")]),
    ]
    merged = apply_vertical_merge(rows)
    assert merged[0].cells[0].rowspan == 2
    assert merged[1].cells[0].vmerge_continue is True


def test_advanced_tables_parser(fixtures_dir):
    source = (fixtures_dir / "advanced-tables.md").read_text(encoding="utf-8")
    doc = MarkdownParser().parse(source)
    tables = [block for block in doc.children if block.type == "table"]
    assert len(tables) == 5
    assert table_logical_column_count(tables[2].rows) == 3
    assert tables[2].rows[1].cells[0].colspan == 2
    assert tables[3].rows[1].cells[0].rowspan == 3
    assert tables[0].rows[1].cells[0].bg == "FFF2CC"
    assert tables[1].rows[1].cells[0].valign == "center"
