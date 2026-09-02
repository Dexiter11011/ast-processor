"""Section break block element handler."""

from __future__ import annotations

from md2docx.ast.types import SectionBreak
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.errors import TemplateModeError
from md2docx.processor.context import ProcessingContext
from md2docx.sections.layout_resolver import layout_from_spec


class SectionBreakHandler:
    """Start a new document section with optional layout change."""

    def process(self, node: SectionBreak, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.template_mode:
            raise TemplateModeError("section breaks are not supported with --template")
        layout = layout_from_spec(node.layout_spec)
        context.sections.add_section(layout, context.document.body_children)
