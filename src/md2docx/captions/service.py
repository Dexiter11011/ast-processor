"""Caption rendering service — internal API for figures, tables, and cross-references."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption, Figure, TableWithCaption
from md2docx.captions.naming import caption_bookmark_name
from md2docx.captions.sequence import SequenceManager
from md2docx.fields.ref_style import RefStyle
from md2docx.ooxml import api
from md2docx.ooxml.image_resolver import resolve_image_path
from md2docx.processor.errors import ImageNotFoundError
from md2docx.references.reference import CrossReference

if TYPE_CHECKING:
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext


@dataclass
class CaptionService:
    """Render captioned figures/tables and caption cross-references."""

    sequence: SequenceManager = field(default_factory=SequenceManager)
    _slug_counts: dict[str, int] = field(default_factory=dict)
    _caption_bookmarks: dict[tuple[CaptionKind, str], str] = field(default_factory=dict)

    def register_captions(self, document, context: ProcessingContext) -> None:
        """Pre-register caption bookmarks and navigation targets for forward references."""
        for node in document.children:
            if isinstance(node, Figure) and node.caption is not None:
                self._ensure_caption_registered(node.caption, context)
            elif isinstance(node, TableWithCaption) and node.caption is not None:
                self._ensure_caption_registered(node.caption, context)

    def _caption_bookmark_for(self, caption: Caption) -> str:
        key = (caption.kind, caption.text)
        if key not in self._caption_bookmarks:
            self._caption_bookmarks[key] = caption_bookmark_name(
                caption.kind,
                caption.text,
                self._slug_counts,
            )
        return self._caption_bookmarks[key]

    def _ensure_caption_registered(self, caption: Caption, context: ProcessingContext) -> None:
        bookmark_name = self._caption_bookmark_for(caption)
        if context.bookmarks.resolve(bookmark_name) is None:
            bookmark_id = context.bookmarks.allocate_id()
            context.bookmarks.register(bookmark_name, bookmark_id=bookmark_id)
        label = self.sequence.label(caption.kind)
        if caption.kind is CaptionKind.FIGURE:
            context.navigation.register_figure(bookmark_name=bookmark_name, label=label)
        else:
            context.navigation.register_table(bookmark_name=bookmark_name, label=label)

    def render_figure(self, node: Figure, context: ProcessingContext, processor: AstProcessor) -> None:
        """Emit image paragraph then caption with SEQ Figure and bookmark."""
        del processor
        self._render_image(node.image, context)
        if node.caption is not None:
            self._render_caption(node.caption, context)

    def render_table_with_caption(
        self,
        node: TableWithCaption,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        """Emit caption above table with SEQ Table and bookmark."""
        if node.caption is not None:
            self._render_caption(node.caption, context)
        context.table_collector = []
        for row in node.table.rows:
            processor.process(row, context)
        table_style_id = context.styles.resolve("table")
        context.document.add_table(
            node.table,
            context.table_collector,
            table_style_id=table_style_id,
            table_presentation=context.styles.table_presentation(),
        )
        context.document.add_table_separator()
        context.table_collector = None

    def render_cross_reference(self, ref: CrossReference, context: ProcessingContext) -> None:
        """Emit a paragraph referencing a captioned object via REF."""
        bookmark_name = context.references.validate_cross_reference(ref)
        style_id = context.styles.resolve("normal")
        label = f"{self.sequence.label(ref.kind)} " if ref.kind is not None else ""
        paragraph = api.caption_reference_paragraph(
            context.fields,
            label=label,
            bookmark_name=bookmark_name,
            bookmarks=context.bookmarks,
            prefix=ref.prefix,
            style_id=style_id,
            ref_style=RefStyle.CAPTION if ref.kind is not None else RefStyle.HEADING,
        )
        context.document.add_body_element(paragraph)

    def _render_image(self, image, context: ProcessingContext) -> None:
        image_path = resolve_image_path(image.src, context.source_dir)
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

    def _render_caption(self, caption: Caption, context: ProcessingContext) -> None:
        bookmark_name = self._caption_bookmark_for(caption)
        existing = context.bookmarks.resolve(bookmark_name)
        if existing is not None:
            bookmark_id = existing.id
        else:
            bookmark_id = context.bookmarks.allocate_id()
            context.bookmarks.register(bookmark_name, bookmark_id=bookmark_id)
            label = self.sequence.label(caption.kind)
            if caption.kind is CaptionKind.FIGURE:
                context.navigation.register_figure(bookmark_name=bookmark_name, label=label)
            else:
                context.navigation.register_table(bookmark_name=bookmark_name, label=label)
        style_id = context.styles.resolve("caption")
        label_text = f"{self.sequence.label(caption.kind)} "
        seq_runs = self.sequence.seq_field_runs(caption.kind, context.fields)
        content_runs = [api.run(caption.text)] if caption.text else []
        paragraph = api.caption_paragraph(
            label=label_text,
            seq_runs=seq_runs,
            separator=". ",
            content_runs=content_runs,
            style_id=style_id,
            bookmark_name=bookmark_name,
            bookmark_id=bookmark_id,
        )
        context.document.add_body_element(paragraph)
