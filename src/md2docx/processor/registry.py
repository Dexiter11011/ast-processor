"""Handler registry for AST node types."""

from __future__ import annotations

from md2docx.processor.element_handler import ElementHandler
from md2docx.processor.errors import UnsupportedNodeError


class HandlerRegistry:
    """Maps AST node type strings to element handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ElementHandler] = {}

    def register(self, node_type: str, handler: ElementHandler) -> HandlerRegistry:
        """Register a handler for *node_type*. Returns self for chaining."""
        self._handlers[node_type] = handler
        return self

    def get(self, node_type: str) -> ElementHandler:
        handler = self._handlers.get(node_type)
        if handler is None:
            raise UnsupportedNodeError(node_type)
        return handler

    def has(self, node_type: str) -> bool:
        return node_type in self._handlers

    def registered_types(self) -> frozenset[str]:
        return frozenset(self._handlers)
