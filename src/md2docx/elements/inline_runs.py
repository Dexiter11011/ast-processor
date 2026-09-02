"""Shared inline run collection for block handlers."""

from __future__ import annotations

from lxml import etree

from md2docx.ast.types import AstNode
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


def collect_runs(node: AstNode, context: ProcessingContext, processor: AstProcessor) -> list[etree._Element]:
    """Process inline children and return collected w:r elements."""
    context.run_collector = []
    processor.process_children(node, context)
    runs = context.run_collector
    context.run_collector = None
    return runs
