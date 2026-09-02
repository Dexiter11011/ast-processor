"""ParagraphHandler tests."""

from md2docx.ast.types import Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.elements.paragraph import ParagraphHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_paragraph_handler_produces_single_paragraph_with_run():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    ParagraphHandler().process(
        Paragraph(children=[Text(value="Hello world")]),
        ctx,
        processor,
    )

    assert len(ctx.document.body_children) == 1
    p = ctx.document.body_children[0]
    assert p.tag == f"{{{W_NS}}}p"
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 1
    text_el = runs[0].find(f"{{{W_NS}}}t")
    assert text_el is not None
    assert text_el.text == "Hello world"
