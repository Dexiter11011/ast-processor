"""Immutable semantic inline content models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class FieldKind(str, Enum):
    PAGE = "page"
    NUMPAGES = "numpages"
    DATE = "date"
    AUTHOR = "author"
    TITLE = "title"
    REF = "ref"
    SEQ = "seq"


class ReferenceKind(str, Enum):
    FIGURE = "figure"
    TABLE = "table"
    HEADING = "heading"


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Bold:
    children: tuple[InlineContent, ...]


@dataclass(frozen=True)
class Italic:
    children: tuple[InlineContent, ...]


@dataclass(frozen=True)
class Strike:
    children: tuple[InlineContent, ...]


@dataclass(frozen=True)
class InlineCode:
    children: tuple[InlineContent, ...]


@dataclass(frozen=True)
class LineBreak:
    pass


@dataclass(frozen=True)
class Hyperlink:
    children: tuple[InlineContent, ...]
    url: str = ""
    anchor: str = ""


@dataclass(frozen=True)
class FieldInline:
    kind: FieldKind
    target: str = ""
    sequence_name: str = ""


InlineContent = Union[
    Text,
    Bold,
    Italic,
    Strike,
    InlineCode,
    LineBreak,
    Hyperlink,
    FieldInline,
]
