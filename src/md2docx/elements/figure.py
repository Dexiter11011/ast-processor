"""Figure element handler."""

from __future__ import annotations

from md2docx.captions.model import Figure
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class FigureHandler:
    """Convert a Figure AST node into image + captioned SEQ field."""

    def process(self, node: Figure, context: ProcessingContext, processor: AstProcessor) -> None:
        context.captions.render_figure(node, context, processor)
