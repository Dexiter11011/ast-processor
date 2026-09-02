"""Element handler protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from md2docx.ast.types import AstNode
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext


class ElementHandler(Protocol):
    """Process a single AST node type."""

    def process(
        self,
        node: AstNode,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        """Convert one AST node into OOXML via the processing context."""
        ...
