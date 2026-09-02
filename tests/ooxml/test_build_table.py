"""OOXML table builder tests."""

from md2docx.ast.types import Table, TableCell, TableRow
from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.run import build_run
from md2docx.ooxml.table import build_table
from md2docx.ooxml.text import build_text
from tests.helpers import W_NS


def test_build_table_creates_grid_and_cells():
    table = Table(
        rows=[
            TableRow(cells=[TableCell(), TableCell()]),
            TableRow(cells=[TableCell(), TableCell()]),
        ]
    )
    rows = [
        [build_paragraph([build_run([build_text("A")])]), build_paragraph([build_run([build_text("B")])])],
        [build_paragraph([build_run([build_text("1")])]), build_paragraph([build_run([build_text("2")])])],
    ]
    tbl = build_table(table, rows)
    assert tbl.tag == f"{{{W_NS}}}tbl"
    assert len(tbl.findall(f".//{{{W_NS}}}gridCol")) == 2
    assert len(tbl.findall(f".//{{{W_NS}}}tr")) == 2
    assert [t.text for t in tbl.findall(f".//{{{W_NS}}}t")] == ["A", "B", "1", "2"]
    assert tbl.find(f".//{{{W_NS}}}tblBorders") is not None
