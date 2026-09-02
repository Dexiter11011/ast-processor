"""Table row element handler."""

from __future__ import annotations

from md2docx.ast.types import TableRow
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TableRowHandler:
    """Collect table cells for the current row."""

    def process(self, node: TableRow, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.table_collector is None:
            raise RuntimeError("TableRowHandler requires an active table_collector")
        context.table_row_collector = []
        for cell in node.cells:
            processor.process(cell, context)
        context.table_collector.append(context.table_row_collector)
        context.table_row_collector = None
