"""Heading block element handler."""

from __future__ import annotations

from md2docx.ast.types import Heading
from md2docx.elements.inline_runs import collect_runs
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class HeadingHandler:
    """Convert a Heading AST node into a styled w:p with an optional bookmark."""

    def process(self, node: Heading, context: ProcessingContext, processor: AstProcessor) -> None:
        runs = collect_runs(node, context, processor)
        style_id = context.styles.resolve("heading", level=node.level)
        bookmark = context.bookmarks.next_heading_bookmark()
        if bookmark is not None:
            element = api.heading(
                runs,
                style_id=style_id,
                bookmark_name=bookmark.name,
                bookmark_id=bookmark.id,
            )
            context.document.add_body_element(element)
            return
        context.document.add_heading(runs, style_id=style_id)
