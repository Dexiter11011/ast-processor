"""Code block element tests."""

from md2docx.ast.types import CodeBlock
from md2docx.elements.code_block import CodeBlockHandler
from md2docx.ooxml.code_block import CODE_BLOCK_STYLE
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_code_block_handler_uses_style_without_inline_fonts():
    ctx = ProcessingContext.create_default()
    CodeBlockHandler().process(CodeBlock(value='print("hello")'), ctx, None)
    p = ctx.document.body_children[0]
    assert p.find(f".//{{{W_NS}}}pStyle").get(f"{{{W_NS}}}val") == CODE_BLOCK_STYLE
    run = p.find(f"{{{W_NS}}}r")
    assert run.find(f".//{{{W_NS}}}rFonts") is None
    assert run.find(f".//{{{W_NS}}}t").text == 'print("hello")'
