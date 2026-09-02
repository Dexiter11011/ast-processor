"""Page break block element handler."""

from __future__ import annotations

from md2docx.ast.types import PageBreak
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class PageBreakHandler:
    """Insert a page break (not a section break)."""

    def process(self, node: PageBreak, context: ProcessingContext, processor: AstProcessor) -> None:
        context.document.add_page_break()
