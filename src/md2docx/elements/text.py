"""Text inline element handler."""

from __future__ import annotations

from md2docx.ast.types import Text
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TextHandler:
    """Convert a Text AST node into a w:r and append to the run collector."""

    def process(self, node: Text, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("TextHandler requires an active run_collector (inside a block handler)")
        formatting = context.render_context.formatting
        r_style = context.styles.resolve_character("inline_code") if formatting.code else ""
        context.run_collector.append(
            api.run_from_formatting(node.value, formatting, r_style=r_style)
        )
