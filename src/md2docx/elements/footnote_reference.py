"""Footnote reference inline element handler."""

from __future__ import annotations

from md2docx.ast.types import FootnoteReference
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class FootnoteReferenceHandler:
    """Convert a FootnoteReference AST node into w:footnoteReference."""

    def process(
        self,
        node: FootnoteReference,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        if context.run_collector is None:
            raise RuntimeError(
                "FootnoteReferenceHandler requires an active run_collector (inside a block handler)"
            )
        footnote_id = context.footnotes.footnote_id(node.label)
        context.run_collector.append(api.footnote_reference_run(footnote_id))
