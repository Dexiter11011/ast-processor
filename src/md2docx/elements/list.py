"""List block element handler."""

from __future__ import annotations

from md2docx.ast.types import List
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.styles import semantic as S


class ListHandler:
    """Convert a List AST node using Word numbering."""

    def process(self, node: List, context: ProcessingContext, processor: AstProcessor) -> None:
        at_top_level = context.list_style is None
        if (
            at_top_level
            and context.document.body_children
            and api.is_active_list_paragraph(context.document.body_children[-1])
        ):
            context.document.add_list_separator()

        saved_style = context.list_style
        saved_ordered = context.list_ordered
        saved_level = context.list_level
        saved_num_id = context.list_num_id

        context.list_level = 0 if at_top_level else saved_level + 1
        context.list_style = S.LIST_PARAGRAPH
        context.list_ordered = node.ordered

        if at_top_level:
            context.list_num_id = context.numbering.allocate_num_id(ordered=node.ordered)
        elif saved_num_id is not None and saved_ordered == node.ordered:
            context.list_num_id = saved_num_id
        elif saved_ordered != node.ordered:
            context.list_num_id = context.numbering.allocate_num_id(
                ordered=node.ordered,
                restart=True,
                restart_ilvl=context.list_level,
            )
        else:
            context.list_num_id = context.numbering.num_id_for_list(ordered=node.ordered)

        for item in node.items:
            processor.process(item, context)

        context.list_style = saved_style
        context.list_ordered = saved_ordered
        context.list_level = saved_level
        context.list_num_id = saved_num_id
