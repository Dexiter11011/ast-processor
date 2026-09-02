"""Handler semantic style resolution tests."""

from __future__ import annotations

from typing import Optional

from md2docx.ast.types import BlockQuote, CodeBlock, Document, Heading, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.styles import semantic as S
from tests.helpers import W_NS


def _p_style(paragraph) -> Optional[str]:
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    return p_style.get(f"{{{W_NS}}}val") if p_style is not None else None


def test_heading_handler_uses_heading1():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Heading(level=1, children=[Text(value="Hello")])])
    processor.process_document(doc, ctx)
    assert _p_style(ctx.document.body_children[0]) == "Heading1"
    assert ctx.styles.resolve_semantic("heading", level=1) == S.HEADING1


def test_paragraph_handler_uses_normal():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Paragraph(children=[Text(value="Hello")])])
    processor.process_document(doc, ctx)
    assert _p_style(ctx.document.body_children[0]) == "Normal"


def test_blockquote_handler_uses_quote():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[BlockQuote(children=[Paragraph(children=[Text(value="Hello")])])])
    processor.process_document(doc, ctx)
    assert _p_style(ctx.document.body_children[0]) == "Quote"


def test_code_block_handler_uses_code_block_style():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[CodeBlock(value='print("hello")', language="python")])
    processor.process_document(doc, ctx)
    assert _p_style(ctx.document.body_children[0]) == "NoSpacing"
    assert ctx.styles.resolve_semantic("code_block") == S.CODE_BLOCK
