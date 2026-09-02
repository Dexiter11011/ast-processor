"""Footer directive handler."""

from __future__ import annotations

from md2docx.ast.types import FooterDirective
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.errors import TemplateModeError
from md2docx.processor.context import ProcessingContext


class FooterDirectiveHandler:
    """Set footer content for the current section."""

    def process(self, node: FooterDirective, context: ProcessingContext, processor: AstProcessor) -> None:
        if context.template_mode:
            raise TemplateModeError("footer directives are not supported with --template")
        style_id = context.styles.resolve("normal")
        directive = node.text.strip().lower()
        if directive == "page-numbers":
            paragraph = api.footer_page_numbers_paragraph(context.fields, style_id=style_id)
        else:
            paragraph = api.paragraph([api.run(node.text)], style_id=style_id)
        context.sections.add_current_footer_paragraphs([paragraph])
