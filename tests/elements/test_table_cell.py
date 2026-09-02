"""TableCellHandler unit tests."""

import pytest

from md2docx.ast.types import Document, Paragraph, Table, TableCell, TableRow, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_table_cell_collects_paragraphs():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Table(
                rows=[
                    TableRow(
                        cells=[
                            TableCell(
                                children=[
                                    Paragraph(children=[Text(value="Line 1")]),
                                    Paragraph(children=[Text(value="Line 2")]),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    processor.process_document(doc, ctx)
    tbl = ctx.document.body_children[0]
    texts = [t.text for t in tbl.findall(f".//{{{W_NS}}}t")]
    assert texts == ["Line 1", "Line 2"]


def test_table_cell_without_row_collector_raises():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    cell = TableCell(children=[Paragraph(children=[Text(value="X")])])
    with pytest.raises(RuntimeError, match="table_row_collector"):
        processor.process(cell, ctx)
