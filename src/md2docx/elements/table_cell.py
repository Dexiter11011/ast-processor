"""Table cell element handler."""

from __future__ import annotations

from md2docx.ast.types import TableCell
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TableCellHandler:
    """Convert cell block children into w:p elements for the current row."""

    def process(self, node: TableCell, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.table_row_collector is None:
            raise RuntimeError("TableCellHandler requires an active table_row_collector")
        context.in_table_cell = True
        context.table_cell_collector = []
        processor.process_children(node, context)
        context.table_row_collector.append(context.table_cell_collector)
        context.table_cell_collector = None
        context.in_table_cell = False
