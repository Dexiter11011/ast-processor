"""Code block element handler."""

from __future__ import annotations

from md2docx.ast.types import CodeBlock
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class CodeBlockHandler:
    """Convert a CodeBlock AST node into a monospace w:p."""

    def process(self, node: CodeBlock, context: ProcessingContext, processor: AstProcessor) -> None:
        style_id = context.styles.resolve("code_block")
        context.document.add_code_block(node.value, style_id=style_id)
