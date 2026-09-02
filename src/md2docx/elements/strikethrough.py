"""Strikethrough inline element handler."""

from __future__ import annotations

from md2docx.ast.types import Strikethrough
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class StrikethroughHandler:
    """Convert a Strikethrough AST node by deriving strike formatting for children."""

    def process(self, node: Strikethrough, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("StrikethroughHandler requires an active run_collector (inside a block handler)")
        child_context = context.render_context.derive(
            formatting=context.render_context.formatting.with_strike()
        )
        with context.push_render_context(child_context):
            processor.process_children(node, context)
