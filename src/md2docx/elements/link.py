"""Link inline element handler."""

from __future__ import annotations

from md2docx.ast.types import Link
from md2docx.elements.inline_format import collect_nested_runs
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class LinkHandler:
    """Convert a Link AST node into w:hyperlink (external rel or internal anchor)."""

    def process(self, node: Link, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.run_collector is None:
            raise RuntimeError("LinkHandler requires an active run_collector (inside a block handler)")
        nested = collect_nested_runs(node, context, processor, handler_name="LinkHandler")
        link = context.styles.link_presentation()
        link_kwargs = {
            "link_color": link.color,
            "link_underline": link.underline,
        }
        if node.is_internal:
            anchor = context.references.resolve_link_anchor(node.bookmark_name)
            if anchor is None:
                context.bookmarks.record_broken_target(node.bookmark_name)
                context.run_collector.extend(nested)
                return
            context.run_collector.append(api.hyperlink(nested, anchor=anchor, **link_kwargs))
            return
        rel_id = context.relationships.add_external_hyperlink(node.url)
        context.run_collector.append(api.hyperlink(nested, rel_id=rel_id, **link_kwargs))
