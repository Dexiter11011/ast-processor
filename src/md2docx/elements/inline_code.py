"""Inline code element handler."""

from __future__ import annotations

from md2docx.ast.types import InlineCode
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class InlineCodeHandler:
    """Convert an InlineCode AST node into a styled w:r."""

    def process(self, node: InlineCode, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("InlineCodeHandler requires an active run_collector (inside a block handler)")
        formatting = context.render_context.formatting.with_code()
        r_style = context.styles.resolve_character("inline_code")
        context.run_collector.append(
            api.run_from_formatting(node.value, formatting, r_style=r_style)
        )
