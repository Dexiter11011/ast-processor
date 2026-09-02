"""Shared helpers for inline formatting handlers."""

from __future__ import annotations

from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


def collect_nested_runs(
    node,
    context: ProcessingContext,
    processor: AstProcessor,
    *,
    handler_name: str,
) -> list:
    """Process inline children into a temporary run collector."""
    if context.run_collector is None:
        raise RuntimeError(f"{handler_name} requires an active run_collector (inside a block handler)")
    nested: list = []
    parent_collector = context.run_collector
    context.run_collector = nested
    processor.process_children(node, context)
    context.run_collector = parent_collector
    return nested
