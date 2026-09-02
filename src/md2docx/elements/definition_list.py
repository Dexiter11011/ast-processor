"""Definition list block element handler."""

from __future__ import annotations

from md2docx.ast.types import DefinitionList, Paragraph
from md2docx.elements.inline_runs import collect_runs
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.styles import semantic as S

class DefinitionListHandler:
    """Render definition lists as styled term and indented description paragraphs."""

    def process(
        self,
        node: DefinitionList,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        for item in node.items:
            bold_context = context.render_context.derive(
                formatting=context.render_context.formatting.with_bold()
            )
            with context.push_render_context(bold_context):
                term_runs = collect_runs(Paragraph(children=item.term), context, processor)
            context.document.add_body_element(
                api.paragraph(
                    term_runs,
                    style_id=context.styles.to_ooxml(S.DEFINITION_TERM),
                )
            )
            saved_block_style = context.block_style
            context.block_style = S.DEFINITION_DESCRIPTION
            try:
                for block in item.description:
                    processor.process(block, context)
            finally:
                context.block_style = saved_block_style
