"""TextHandler tests."""

import pytest

from md2docx.ast.types import Text
from md2docx.elements import create_default_registry
from md2docx.elements.text import TextHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_text_handler_appends_run_to_collector():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    processor = AstProcessor(create_default_registry())
    TextHandler().process(Text(value="Hello world"), ctx, processor)

    assert len(ctx.run_collector) == 1
    run = ctx.run_collector[0]
    assert run.tag == f"{{{W_NS}}}r"
    text_el = run.find(f"{{{W_NS}}}t")
    assert text_el is not None
    assert text_el.text == "Hello world"


def test_text_handler_requires_collector():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    with pytest.raises(RuntimeError, match="run_collector"):
        TextHandler().process(Text(value="Hi"), ctx, processor)
