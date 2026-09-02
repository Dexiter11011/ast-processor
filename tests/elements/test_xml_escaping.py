"""Element handler tests for XML special characters."""

from md2docx.ast.types import CodeBlock, Document, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_text_handler_preserves_special_characters():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Paragraph(children=[Text(value='A & B <tag> "quote" \'apos\'')])])
    processor.process_document(doc, ctx)

    text_el = ctx.document.body_children[0].find(f".//{{{W_NS}}}t")
    assert text_el.text == 'A & B <tag> "quote" \'apos\''


def test_code_block_handler_preserves_special_characters():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[CodeBlock(value="x < y && z\n", language="text")])
    processor.process_document(doc, ctx)

    texts = [t.text for t in ctx.document.body_children[0].findall(f".//{{{W_NS}}}t")]
    assert texts == ["x < y && z"]
