"""Blockquote element tests."""

from typing import Optional

from md2docx.ast.types import BlockQuote, Document, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def _paragraph_style(paragraph) -> Optional[str]:
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    if p_style is None:
        return None
    return p_style.get(f"{{{W_NS}}}val")


def test_blockquote_applies_quote_style():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            BlockQuote(
                children=[
                    Paragraph(children=[Text(value="Quote line one.")]),
                    Paragraph(children=[Text(value="Quote line two.")]),
                ]
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    for paragraph in ctx.document.body_children:
        assert _paragraph_style(paragraph) == "Quote"
