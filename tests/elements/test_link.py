"""LinkHandler tests."""

import pytest

from md2docx.ast.types import Link, Text
from md2docx.elements import create_default_registry
from md2docx.elements.link import LinkHandler
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import R_NS, W_NS


def test_link_handler_builds_hyperlink():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    processor = AstProcessor(create_default_registry())
    LinkHandler().process(
        Link(url="https://openai.com", children=[Text(value="OpenAI")]),
        ctx,
        processor,
    )

    assert len(ctx.run_collector) == 1
    hyper = ctx.run_collector[0]
    assert hyper.tag == f"{{{W_NS}}}hyperlink"
    assert hyper.get(f"{{{R_NS}}}id") == "rId2"
    run = hyper.find(f"{{{W_NS}}}r")
    assert run is not None
    assert run.find(f"{{{W_NS}}}t").text == "OpenAI"
    r_pr = run.find(f"{{{W_NS}}}rPr")
    assert r_pr.find(f"{{{W_NS}}}u") is not None
    assert r_pr.find(f"{{{W_NS}}}color").get(f"{{{W_NS}}}val") == "0563C1"


def test_link_handler_requires_collector():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    with pytest.raises(RuntimeError, match="run_collector"):
        LinkHandler().process(Link(url="https://x.com", children=[Text(value="x")]), ctx, processor)


def test_link_handler_internal_uses_anchor():
    ctx = ProcessingContext.create_default()
    from md2docx.ast.types import Document, Heading

    ctx.bookmarks.register_headings(
        Document(children=[Heading(level=1, children=[Text(value="Intro")])])
    )
    ctx.run_collector = []
    processor = AstProcessor(create_default_registry())
    LinkHandler().process(
        Link(url="#intro", children=[Text(value="Go")]),
        ctx,
        processor,
    )
    hyper = ctx.run_collector[0]
    assert hyper.get(f"{{{W_NS}}}anchor") == "intro"
    assert hyper.get(f"{{{R_NS}}}id") is None
