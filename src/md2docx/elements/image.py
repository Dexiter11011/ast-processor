"""Image block element handler."""

from __future__ import annotations

from md2docx.ast.types import Image
from md2docx.ooxml import api
from md2docx.ooxml.image_resolver import resolve_image_path
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.processor.errors import ImageNotFoundError


class ImageHandler:
    """Convert an Image AST node into w:drawing paragraph(s)."""

    def process(self, node: Image, context: ProcessingContext, processor: AstProcessor) -> None:
        del processor
        image_path = resolve_image_path(node.src, context.source_dir)
        if not image_path.is_file():
            raise ImageNotFoundError(str(image_path))

        data = image_path.read_bytes()
        extension = image_path.suffix.lower().lstrip(".") or "png"
        media_path = context.media.add_image(data, extension)
        rel_id = context.relationships.add_image_relationship(api.media_filename(media_path))
        width_px, height_px = api.image_size(data)
        width_emu, height_emu = api.scale_image(width_px, height_px)
        doc_pr_id = context.media.next_doc_pr_id()
        context.document.add_image(
            rel_id=rel_id,
            width_emu=width_emu,
            height_emu=height_emu,
            doc_pr_id=doc_pr_id,
            name=f"Picture {doc_pr_id}",
        )
        if node.alt:
            context.document.add_alt_text(node.alt)
