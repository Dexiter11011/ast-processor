"""Header directive handler."""

from __future__ import annotations

from md2docx.ast.types import HeaderDirective
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.errors import TemplateModeError
from md2docx.processor.context import ProcessingContext


class HeaderDirectiveHandler:
    """Set header content for the current section."""

    def process(self, node: HeaderDirective, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.template_mode:
            raise TemplateModeError("header directives are not supported with --template")
        style_id = context.styles.resolve("normal")
        directive = node.text.strip().lower()
        if directive == "author-field":
            paragraph = api.header_author_field_paragraph(context.fields, style_id=style_id)
        elif directive == "title-field":
            paragraph = api.header_title_field_paragraph(context.fields, style_id=style_id)
        elif directive == "date-field":
            paragraph = api.paragraph([context.fields.date_field()], style_id=style_id)
        else:
            paragraph = api.paragraph([api.run(node.text)], style_id=style_id)
        context.sections.add_current_header_paragraphs([paragraph])
