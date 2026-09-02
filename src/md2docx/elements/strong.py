"""Strong inline element handler."""

from __future__ import annotations

from md2docx.ast.types import Strong
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class StrongHandler:
    """Convert a Strong AST node by deriving bold formatting for children."""

    def process(self, node: Strong, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("StrongHandler requires an active run_collector (inside a block handler)")
        child_context = context.render_context.derive(
            formatting=context.render_context.formatting.with_bold()
        )
        with context.push_render_context(child_context):
            processor.process_children(node, context)
