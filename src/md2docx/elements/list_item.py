"""List item element handler."""

from __future__ import annotations

from md2docx.ast.types import ListItem
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class ListItemHandler:
    """Process block children of a list item."""

    def process(self, node: ListItem, context: ProcessingContext, processor: AstProcessor) -> None:
        if node.checked is not None:
            context.task_checkbox_pending = node.checked
        for child in node.children:
            processor.process(child, context)
        context.task_checkbox_pending = None
