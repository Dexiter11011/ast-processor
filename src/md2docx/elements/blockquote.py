"""Blockquote block element handler."""

from __future__ import annotations

from md2docx.ast.types import BlockQuote
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class BlockQuoteHandler:
    """Convert a BlockQuote AST node by styling child paragraphs as Quote."""

    def process(self, node: BlockQuote, context: ProcessingContext, processor: AstProcessor) -> None:
        saved_style = context.block_style
        context.block_style = context.styles.resolve_semantic("blockquote")
        for child in node.children:
            processor.process(child, context)
        context.block_style = saved_style
