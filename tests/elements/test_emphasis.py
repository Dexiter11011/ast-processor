"""EmphasisHandler tests."""

import pytest

from md2docx.ast.types import Emphasis, Text
from md2docx.elements import create_default_registry
from md2docx.elements.emphasis import EmphasisHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_emphasis_handler_applies_italic():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    processor = AstProcessor(create_default_registry())
    EmphasisHandler().process(Emphasis(children=[Text(value="world")]), ctx, processor)

    assert len(ctx.run_collector) == 1
    run = ctx.run_collector[0]
    r_pr = run.find(f"{{{W_NS}}}rPr")
    assert r_pr is not None
    assert r_pr.find(f"{{{W_NS}}}i") is not None
    assert run.find(f"{{{W_NS}}}t").text == "world"


def test_emphasis_handler_requires_collector():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    with pytest.raises(RuntimeError, match="run_collector"):
        EmphasisHandler().process(Emphasis(children=[Text(value="x")]), ctx, processor)
