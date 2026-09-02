"""HeadingHandler tests."""

from md2docx.ast.types import Heading, Text
from md2docx.elements import create_default_registry
from md2docx.elements.heading import HeadingHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_heading_handler_applies_style():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    HeadingHandler().process(Heading(level=2, children=[Text(value="Heading 2")]), ctx, processor)

    assert len(ctx.document.body_children) == 1
    p = ctx.document.body_children[0]
    p_pr = p.find(f"{{{W_NS}}}pPr")
    assert p_pr is not None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    assert p_style is not None
    assert p_style.get(f"{{{W_NS}}}val") == "Heading2"
    text_el = p.find(f".//{{{W_NS}}}t")
    assert text_el is not None
    assert text_el.text == "Heading 2"
