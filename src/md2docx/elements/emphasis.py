"""Emphasis inline element handler."""

from __future__ import annotations

from md2docx.ast.types import Emphasis
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class EmphasisHandler:
    """Convert an Emphasis AST node by deriving italic formatting for children."""

    def process(self, node: Emphasis, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("EmphasisHandler requires an active run_collector (inside a block handler)")
        child_context = context.render_context.derive(
            formatting=context.render_context.formatting.with_italic()
        )
        with context.push_render_context(child_context):
            processor.process_children(node, context)
