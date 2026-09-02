"""Hard line break inline element handler."""

from __future__ import annotations

from md2docx.ast.types import LineBreak
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class LineBreakHandler:
    """Convert a LineBreak AST node into a hard break inside the current paragraph."""

    def process(self, node: LineBreak, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("LineBreakHandler requires an active run_collector (inside a block handler)")
        context.run_collector.append(api.line_break())
