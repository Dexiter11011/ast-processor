"""Image element tests."""

from pathlib import Path

from md2docx.ast.types import Document, Image
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_image_handler_embeds_media(fixtures_dir: Path):
    ctx = ProcessingContext.create_default(source_dir=fixtures_dir)
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Image(src="logo.png", alt="Logo")])
    processor.process_document(doc, ctx)

    assert len(ctx.document.body_children) == 2
    assert ctx.document.body_children[0].find(f".//{{{W_NS}}}drawing") is not None
    assert ctx.document.body_children[1].find(f".//{{{W_NS}}}t").text == "Logo"
    assert len(ctx.media.parts) == 1
    assert any(path.startswith("word/media/image1.") for path in ctx.media.parts)
