"""Table block element handler."""

from __future__ import annotations

from md2docx.ast.types import Table
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TableHandler:
    """Convert a Table AST node into a table body element."""

    def process(self, node: Table, context: ProcessingContext, processor: AstProcessor) -> None:
        context.table_collector = []
        for row in node.rows:
            processor.process(row, context)
        table_style_id = context.styles.resolve("table")
        context.document.add_table(
            node,
            context.table_collector,
            table_style_id=table_style_id,
            table_presentation=context.styles.table_presentation(),
        )
        context.document.add_table_separator()
        context.table_collector = None
