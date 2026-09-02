"""Table with caption element handler."""

from __future__ import annotations

from md2docx.captions.model import TableWithCaption
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TableWithCaptionHandler:
    """Convert a TableWithCaption AST node into caption + table."""

    def process(self, node: TableWithCaption, context: ProcessingContext, processor: AstProcessor) -> None:
        context.captions.render_table_with_caption(node, context, processor)
