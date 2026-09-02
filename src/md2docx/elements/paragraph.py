"""Paragraph block element handler."""

from __future__ import annotations

from md2docx.ast.types import Paragraph
from md2docx.elements.inline_runs import collect_runs
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.styles import semantic as S


class ParagraphHandler:
    """Convert a Paragraph AST node into a w:p body element."""

    def process(self, node: Paragraph, context: ProcessingContext, processor: AstProcessor) -> None:
        runs = collect_runs(node, context, processor)
        if context.task_checkbox_pending is not None and context.list_style is not None:
            marker = "☒" if context.task_checkbox_pending else "☐"
            runs = [api.run(f"{marker} ")] + runs
            context.task_checkbox_pending = None
        semantic_style = context.list_style or context.block_style or S.NORMAL
        paragraph = api.paragraph(
            runs,
            style_id=context.styles.to_ooxml(semantic_style),
            num_id=context.list_num_id if context.list_style is not None else None,
            num_level=context.list_level,
            indent_left_twips=context.paragraph_indent_twips,
        )
        if context.in_table_cell:
            if context.table_cell_collector is None:
                raise RuntimeError("ParagraphHandler requires table_cell_collector inside a table cell")
            context.table_cell_collector.append(paragraph)
            return
        context.document.add_body_element(paragraph)
