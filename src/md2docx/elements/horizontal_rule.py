"""Horizontal rule element handler."""

from __future__ import annotations

from md2docx.ast.types import HorizontalRule
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class HorizontalRuleHandler:
    """Convert a HorizontalRule AST node into a bordered w:p."""

    def process(self, node: HorizontalRule, context: ProcessingContext, processor: AstProcessor) -> None:
        context.document.add_horizontal_rule()
