"""Internal adapter from semantic models to existing OOXML pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from lxml import etree

from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption
from md2docx.fields.ref_style import RefStyle
from md2docx.ooxml import api
from md2docx.ooxml.bookmark import wrap_paragraph_with_bookmark
from md2docx.ooxml.image_resolver import resolve_image_path
from md2docx.processor.inline_formatting import InlineFormatting
from md2docx.references.reference import CrossReference as InternalCrossReference
from md2docx.semantic.blocks import (
    BookmarkParagraph,
    BulletList,
    CrossReference,
    Figure,
    ListItem,
    OrderedList,
    Paragraph,
    SemanticBlock,
    SemanticImage,
)
from md2docx.semantic.errors import (
    InvalidFieldError,
    InvalidHyperlinkError,
    InvalidMediaError,
    InvalidReferenceError,
    InvalidStyleError,
)
from md2docx.semantic.fragment import RichDocumentFragment
from md2docx.semantic.inline import (
    Bold,
    FieldInline,
    FieldKind,
    Hyperlink,
    InlineCode,
    InlineContent,
    Italic,
    LineBreak,
    ReferenceKind,
    Strike,
    Text,
)
from md2docx.semantic.validation import (
    validate_bookmark_name,
    validate_external_url,
    validate_internal_anchor,
)
from md2docx.styles import semantic as S

if TYPE_CHECKING:
    from md2docx.semantic.context import SemanticContext


class SemanticRenderer:
    """Render semantic fragments through existing managers and OOXML facade."""

    @classmethod
    def render_to_document(cls, fragment: RichDocumentFragment, context: SemanticContext) -> None:
        for element in cls.render(fragment, context):
            context._processing.document.add_body_element(element)

    @classmethod
    def render(cls, fragment: RichDocumentFragment, context: SemanticContext) -> list[etree._Element]:
        if fragment.empty:
            return []
        elements: list[etree._Element] = []
        for block in fragment.blocks:
            elements.extend(cls._render_block(block, context))
        return elements

    @classmethod
    def _render_block(cls, block: SemanticBlock, context: SemanticContext) -> list[etree._Element]:
        if isinstance(block, Paragraph):
            return [cls._render_paragraph(block, context)]
        if isinstance(block, BookmarkParagraph):
            return [cls._render_bookmark_paragraph(block, context)]
        if isinstance(block, BulletList):
            return cls._render_list(block.items, ordered=False, context=context)
        if isinstance(block, OrderedList):
            return cls._render_list(block.items, ordered=True, context=context)
        if isinstance(block, SemanticImage):
            return cls._build_image_elements(block, context)
        if isinstance(block, Figure):
            return cls._render_figure(block, context)
        if isinstance(block, CrossReference):
            return [cls._render_cross_reference(block, context)]
        raise TypeError(f"unsupported semantic block: {type(block)!r}")

    @classmethod
    def _resolve_style(cls, semantic_id: str, context: SemanticContext) -> str:
        try:
            return context.styles.to_ooxml(semantic_id)
        except KeyError as exc:
            raise InvalidStyleError(f"unknown semantic style: {semantic_id!r}") from exc

    @classmethod
    def _render_paragraph(
        cls,
        block: Paragraph,
        context: SemanticContext,
        *,
        num_id: int | None = None,
        num_level: int = 0,
    ) -> etree._Element:
        runs = cls._render_inline_children(block.children, context)
        return api.paragraph(
            runs,
            style_id=cls._resolve_style(block.style, context),
            num_id=num_id,
            num_level=num_level,
        )

    @classmethod
    def _render_bookmark_paragraph(cls, block: BookmarkParagraph, context: SemanticContext) -> etree._Element:
        validate_bookmark_name(block.name)
        processing = context._processing
        bookmark = processing.bookmarks.register(block.name.strip())
        paragraph = cls._render_paragraph(block.paragraph, context)
        return wrap_paragraph_with_bookmark(paragraph, name=bookmark.name, bookmark_id=bookmark.id)

    @classmethod
    def _render_inline_children(
        cls,
        children: tuple[InlineContent, ...],
        context: SemanticContext,
        *,
        formatting: InlineFormatting | None = None,
    ) -> list[etree._Element]:
        runs: list[etree._Element] = []
        active = formatting or InlineFormatting()
        for child in children:
            runs.extend(cls._render_inline(child, context, formatting=active))
        return runs

    @classmethod
    def _render_inline(
        cls,
        node: InlineContent,
        context: SemanticContext,
        *,
        formatting: InlineFormatting,
    ) -> list[etree._Element]:
        if isinstance(node, Text):
            if not node.value:
                return []
            style_id = context._processing.styles.resolve_character("inline_code") if formatting.code else ""
            return [api.run_from_formatting(node.value, formatting, r_style=style_id)]
        if isinstance(node, Bold):
            return cls._render_inline_children(node.children, context, formatting=formatting.with_bold())
        if isinstance(node, Italic):
            return cls._render_inline_children(node.children, context, formatting=formatting.with_italic())
        if isinstance(node, Strike):
            return cls._render_inline_children(node.children, context, formatting=formatting.with_strike())
        if isinstance(node, InlineCode):
            return cls._render_inline_children(node.children, context, formatting=formatting.with_code())
        if isinstance(node, LineBreak):
            return [api.line_break()]
        if isinstance(node, Hyperlink):
            return cls._render_hyperlink(node, context, formatting=formatting)
        if isinstance(node, FieldInline):
            return cls._render_field_inline(node, context)
        raise TypeError(f"unsupported inline node: {type(node)!r}")

    @classmethod
    def _render_hyperlink(
        cls,
        node: Hyperlink,
        context: SemanticContext,
        *,
        formatting: InlineFormatting,
    ) -> list[etree._Element]:
        nested = cls._render_inline_children(node.children, context, formatting=formatting)
        if not nested:
            return []
        processing = context._processing
        link = processing.styles.link_presentation()
        link_kwargs = {"link_color": link.color, "link_underline": link.underline}
        if node.anchor:
            validate_internal_anchor(node.anchor)
            anchor = processing.references.resolve_link_anchor(node.anchor.lstrip("#"))
            if anchor is None:
                processing.bookmarks.record_broken_target(node.anchor.lstrip("#"))
                return nested
            return [api.hyperlink(nested, anchor=anchor, **link_kwargs)]
        if not node.url:
            raise InvalidHyperlinkError("hyperlink requires url or anchor")
        validate_external_url(node.url)
        rel_id = processing.relationships.add_external_hyperlink(node.url)
        return [api.hyperlink(nested, rel_id=rel_id, **link_kwargs)]

    @classmethod
    def _render_field_inline(cls, node: FieldInline, context: SemanticContext) -> list[etree._Element]:
        processing = context._processing
        fields = processing.fields
        if node.kind is FieldKind.PAGE:
            return [fields.page_field()]
        if node.kind is FieldKind.NUMPAGES:
            return [fields.numpages_field()]
        if node.kind is FieldKind.DATE:
            return [fields.date_field()]
        if node.kind is FieldKind.AUTHOR:
            return [fields.author_field()]
        if node.kind is FieldKind.TITLE:
            return [fields.title_field()]
        if node.kind is FieldKind.REF:
            if not node.target:
                raise InvalidFieldError("REF field requires target bookmark name")
            return fields.ref_field(node.target, bookmarks=processing.bookmarks)
        if node.kind is FieldKind.SEQ:
            if not node.sequence_name:
                raise InvalidFieldError("SEQ field requires sequence_name")
            return fields.seq_field(node.sequence_name)
        raise InvalidFieldError(f"unsupported field kind: {node.kind!r}")

    @classmethod
    def _render_list(
        cls,
        items: tuple[ListItem, ...],
        *,
        ordered: bool,
        context: SemanticContext,
        level: int = 0,
    ) -> list[etree._Element]:
        processing = context._processing
        elements: list[etree._Element] = []
        num_id = processing.numbering.allocate_num_id(ordered=ordered)
        for item in items:
            for block in item.blocks:
                if isinstance(block, Paragraph):
                    elements.append(
                        cls._render_paragraph(
                            Paragraph(style=S.LIST_PARAGRAPH, children=block.children),
                            context,
                            num_id=num_id,
                            num_level=level,
                        )
                    )
                elif isinstance(block, BulletList):
                    elements.extend(cls._render_list(block.items, ordered=False, context=context, level=level + 1))
                elif isinstance(block, OrderedList):
                    elements.extend(cls._render_list(block.items, ordered=True, context=context, level=level + 1))
                else:
                    elements.extend(cls._render_block(block, context))
        return elements

    @classmethod
    def _load_image_bytes(cls, source, context: SemanticContext) -> tuple[bytes, str]:
        processing = context._processing
        if isinstance(source, bytes):
            return source, "png"
        if isinstance(source, (str, Path)):
            path = resolve_image_path(str(source), processing.source_dir)
            if not path.is_file():
                raise InvalidMediaError(f"image not found: {path}")
            extension = path.suffix.lower().lstrip(".") or "png"
            return path.read_bytes(), extension
        raise InvalidMediaError(f"unsupported image source: {type(source)!r}")

    @classmethod
    def _build_image_elements(cls, block: SemanticImage, context: SemanticContext) -> list[etree._Element]:
        processing = context._processing
        data, extension = cls._load_image_bytes(block.source, context)
        media_path = processing.media.add_image(data, extension)
        rel_id = processing.relationships.add_image_relationship(api.media_filename(media_path))
        width_px, height_px = api.image_size(data)
        width_emu, height_emu = api.scale_image(width_px, height_px)
        doc_pr_id = processing.media.next_doc_pr_id()
        elements = [
            api.image_paragraph(
                rel_id=rel_id,
                width_emu=width_emu,
                height_emu=height_emu,
                doc_pr_id=doc_pr_id,
                name=f"Picture {doc_pr_id}",
            )
        ]
        if block.alt:
            elements.append(api.alt_text_paragraph(block.alt))
        return elements

    @classmethod
    def _render_figure(cls, block: Figure, context: SemanticContext) -> list[etree._Element]:
        processing = context._processing
        elements = cls._build_image_elements(block.image, context)
        caption = Caption(kind=CaptionKind.FIGURE, text=block.caption_text)
        processing.captions._ensure_caption_registered(caption, processing)
        bookmark_name = processing.captions._caption_bookmark_for(caption)
        existing = processing.bookmarks.resolve(bookmark_name)
        if existing is not None:
            bookmark_id = existing.id
        else:
            bookmark_id = processing.bookmarks.allocate_id()
            processing.bookmarks.register(bookmark_name, bookmark_id=bookmark_id)
        label = processing.captions.sequence.label(CaptionKind.FIGURE)
        seq_runs = processing.captions.sequence.seq_field_runs(CaptionKind.FIGURE, processing.fields)
        content_runs = [api.run(block.caption_text)] if block.caption_text else []
        elements.append(
            api.caption_paragraph(
                label=f"{label} ",
                seq_runs=seq_runs,
                separator=". ",
                content_runs=content_runs,
                style_id=cls._resolve_style(S.CAPTION, context),
                bookmark_name=bookmark_name,
                bookmark_id=bookmark_id,
            )
        )
        return elements

    @classmethod
    def _render_cross_reference(cls, block: CrossReference, context: SemanticContext) -> etree._Element:
        processing = context._processing
        kind = None
        if block.kind is ReferenceKind.FIGURE:
            kind = CaptionKind.FIGURE
        elif block.kind is ReferenceKind.TABLE:
            kind = CaptionKind.TABLE
        internal = InternalCrossReference(target=block.target, kind=kind, prefix=block.prefix)
        try:
            bookmark_name = processing.references.validate_cross_reference(internal)
        except Exception as exc:
            raise InvalidReferenceError(str(exc)) from exc
        style_id = processing.styles.resolve("normal")
        label = f"{processing.captions.sequence.label(kind)} " if kind is not None else ""
        return api.caption_reference_paragraph(
            processing.fields,
            label=label,
            bookmark_name=bookmark_name,
            bookmarks=processing.bookmarks,
            prefix=block.prefix,
            style_id=style_id,
            ref_style=RefStyle.CAPTION if kind is not None else RefStyle.HEADING,
        )


def coerce_template_fragment(result, context) -> list[etree._Element]:
    from md2docx.semantic.context import SemanticContext

    if isinstance(result, RichDocumentFragment):
        return SemanticRenderer.render(result, SemanticContext.from_processing_context(context))
    if isinstance(result, list):
        return result
    if result is None:
        return []
    raise TypeError("template region renderer must return RichDocumentFragment, list[Element], or None")
