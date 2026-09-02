"""Horizontal rule element tests."""

from md2docx.ast.types import Document, HorizontalRule
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_horizontal_rule_produces_paragraph_border():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[HorizontalRule()])
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 1
    p = ctx.document.body_children[0]
    p_pr = p.find(f"{{{W_NS}}}pPr")
    assert p_pr is not None
    p_bdr = p_pr.find(f"{{{W_NS}}}pBdr")
    assert p_bdr is not None
    bottom = p_bdr.find(f"{{{W_NS}}}bottom")
    assert bottom is not None
    assert bottom.get(f"{{{W_NS}}}val") == "single"
