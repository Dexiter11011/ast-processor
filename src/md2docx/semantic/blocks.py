"""Immutable semantic block content models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from md2docx.semantic.inline import InlineContent, ReferenceKind

MediaSource = Union[Path, bytes, str]


@dataclass(frozen=True)
class Paragraph:
    style: str
    children: tuple[InlineContent, ...]


@dataclass(frozen=True)
class BookmarkParagraph:
    name: str
    paragraph: Paragraph


@dataclass(frozen=True)
class ListItem:
    blocks: tuple[SemanticBlock, ...]


@dataclass(frozen=True)
class BulletList:
    items: tuple[ListItem, ...]


@dataclass(frozen=True)
class OrderedList:
    items: tuple[ListItem, ...]


@dataclass(frozen=True)
class SemanticImage:
    source: MediaSource
    alt: str = ""


@dataclass(frozen=True)
class Figure:
    image: SemanticImage
    caption_text: str
    label: str = ""


@dataclass(frozen=True)
class CrossReference:
    target: str
    kind: ReferenceKind | None = None
    prefix: str = "See "


SemanticBlock = Union[
    Paragraph,
    BookmarkParagraph,
    BulletList,
    OrderedList,
    SemanticImage,
    Figure,
    CrossReference,
]
