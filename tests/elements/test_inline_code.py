"""Inline code element tests."""

from md2docx.ast.types import InlineCode, Paragraph, Text
from md2docx.elements.inline_code import InlineCodeHandler
from md2docx.ooxml.style_ids import CODE
from md2docx.ooxml.run import build_run
from md2docx.ooxml.text import build_text
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_inline_code_handler_uses_character_style():
    ctx = ProcessingContext.create_default()
    ctx.run_collector = []
    InlineCodeHandler().process(InlineCode(value="npm install"), ctx, None)
    run = ctx.run_collector[0]
    r_style = run.find(f".//{{{W_NS}}}rStyle")
    assert r_style is not None
    assert r_style.get(f"{{{W_NS}}}val") == CODE
    assert run.find(f".//{{{W_NS}}}rFonts") is None
