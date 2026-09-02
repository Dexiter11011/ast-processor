"""TableRowHandler unit tests."""

import pytest

from md2docx.ast.types import Document, Paragraph, Table, TableCell, TableRow, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


def test_table_row_collects_cells():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Table(
                rows=[
                    TableRow(
                        cells=[
                            TableCell(children=[Paragraph(children=[Text(value="A")])]),
                            TableCell(children=[Paragraph(children=[Text(value="B")])]),
                        ]
                    )
                ]
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2


def test_table_row_without_table_collector_raises():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    row = TableRow(cells=[TableCell(children=[Paragraph(children=[Text(value="X")])])])
    with pytest.raises(RuntimeError, match="table_collector"):
        processor.process(row, ctx)
