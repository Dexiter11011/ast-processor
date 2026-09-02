"""Strikethrough handler tests."""

from md2docx.ast.types import Strikethrough, Text
from md2docx.elements import create_default_registry
from md2docx.elements.strikethrough import StrikethroughHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_strikethrough_handler_applies_strike():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    processor = AstProcessor(create_default_registry())
    StrikethroughHandler().process(
        Strikethrough(children=[Text(value="deleted")]),
        ctx,
        processor,
    )
    run = ctx.run_collector[0]
    r_pr = run.find(f"{{{W_NS}}}rPr")
    assert r_pr.find(f"{{{W_NS}}}strike") is not None
