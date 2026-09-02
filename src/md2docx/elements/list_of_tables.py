"""List of Tables block element handler."""

from __future__ import annotations

from md2docx.ast.types import ListOfTables
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class ListOfTablesHandler:
    """Insert a Word List of Tables field paragraph."""

    def process(self, node: ListOfTables, context: ProcessingContext, processor: AstProcessor) -> None:
        del node, processor
        context.fields.mark_dynamic_field_used()
        context.document.add_body_element(context.toc.build_lot_paragraph())
