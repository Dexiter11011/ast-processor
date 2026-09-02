"""Table of contents block element handler."""

from __future__ import annotations

from md2docx.ast.types import TableOfContents
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class TableOfContentsHandler:
    """Insert a Word TOC field paragraph at the document level."""

    def process(self, node: TableOfContents, context: ProcessingContext, processor: AstProcessor) -> None:
        from md2docx.toc.definition import TocSpec

        spec = TocSpec(min_level=node.min_level, max_level=node.max_level)
        context.fields.mark_dynamic_field_used()
        context.document.add_body_element(context.toc.build_paragraph(spec))
