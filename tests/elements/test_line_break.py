"""Line break handler tests."""

from md2docx.ast.types import LineBreak, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.elements.line_break import LineBreakHandler
from md2docx.elements.paragraph import ParagraphHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_line_break_handler_emits_w_br():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    LineBreakHandler().process(LineBreak(), ctx, AstProcessor(create_default_registry()))
    assert ctx.run_collector[0].find(f"{{{W_NS}}}br") is not None


def test_paragraph_with_hard_break_in_single_p():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    ParagraphHandler().process(
        Paragraph(children=[Text(value="A"), LineBreak(), Text(value="B")]),
        ctx,
        processor,
    )
    para = ctx.document.body_children[0]
    assert len(para.findall(f".//{{{W_NS}}}br")) == 1
    assert len(para.findall(f"{{{W_NS}}}p")) == 0
