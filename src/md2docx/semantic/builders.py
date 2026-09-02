"""Convenience builders for the public semantic API."""

from __future__ import annotations

from pathlib import Path

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
from md2docx.semantic.validation import normalize_text, validate_external_url, validate_paragraph_children


def fragment(*blocks: SemanticBlock) -> RichDocumentFragment:
    return RichDocumentFragment(blocks)


def paragraph(style: str, *children: InlineContent) -> Paragraph:
    items = tuple(children)
    validate_paragraph_children(items)
    return Paragraph(style=style, children=items)


def text(value: str) -> Text:
    return Text(normalize_text(value))


def bold(*children: InlineContent) -> Bold:
    return Bold(tuple(children))


def italic(*children: InlineContent) -> Italic:
    return Italic(tuple(children))


def strike(*children: InlineContent) -> Strike:
    return Strike(tuple(children))


def inline_code(*children: InlineContent) -> InlineCode:
    return InlineCode(tuple(children))


def line_break() -> LineBreak:
    return LineBreak()


def hyperlink(url: str, *children: InlineContent) -> Hyperlink:
    validate_external_url(url)
    return Hyperlink(children=tuple(children), url=url)


def hyperlink_to(anchor: str, *children: InlineContent) -> Hyperlink:
    return Hyperlink(children=tuple(children), anchor=anchor)


def bookmark(name: str, block: Paragraph) -> BookmarkParagraph:
    return BookmarkParagraph(name=name, paragraph=block)


def page_field() -> FieldInline:
    return FieldInline(kind=FieldKind.PAGE)


def numpages_field() -> FieldInline:
    return FieldInline(kind=FieldKind.NUMPAGES)


def date_field() -> FieldInline:
    return FieldInline(kind=FieldKind.DATE)


def author_field() -> FieldInline:
    return FieldInline(kind=FieldKind.AUTHOR)


def title_field() -> FieldInline:
    return FieldInline(kind=FieldKind.TITLE)


def ref_field(target: str) -> FieldInline:
    return FieldInline(kind=FieldKind.REF, target=target)


def seq_field(sequence_name: str) -> FieldInline:
    return FieldInline(kind=FieldKind.SEQ, sequence_name=sequence_name)


def image(source: Path | bytes | str, *, alt: str = "") -> SemanticImage:
    return SemanticImage(source=source, alt=alt)


def figure(source: Path | bytes | str, *, caption_text: str, alt: str = "") -> Figure:
    return Figure(image=SemanticImage(source=source, alt=alt), caption_text=caption_text)


def cross_reference(
    target: str,
    *,
    kind: ReferenceKind | None = None,
    prefix: str = "See ",
) -> CrossReference:
    return CrossReference(target=target, kind=kind, prefix=prefix)


def list_item(*blocks: SemanticBlock) -> ListItem:
    return ListItem(tuple(blocks))


def bullet_list(*items: ListItem) -> BulletList:
    return BulletList(tuple(items))


def ordered_list(*items: ListItem) -> OrderedList:
    return OrderedList(tuple(items))
