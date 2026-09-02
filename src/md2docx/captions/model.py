"""Semantic caption and captioned-object models."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.ast.types import Image, Table
from md2docx.captions.kinds import CaptionKind
from md2docx.references.reference import CrossReference


@dataclass
class Caption:
    """Caption text and kind — no authoritative sequence number."""

    kind: CaptionKind
    text: str = ""


@dataclass
class Figure:
    """Image with optional caption (Figure semantic object)."""

    type: str = "figure"
    image: Image = field(default_factory=Image)
    caption: Caption | None = None


@dataclass
class TableWithCaption:
    """Table with optional caption above the table."""

    type: str = "table_with_caption"
    table: Table = field(default_factory=Table)
    caption: Caption | None = None


@dataclass
class CrossReferenceBlock:
    """Body block that emits a caption or heading cross-reference."""

    type: str = "cross_reference"
    reference: CrossReference = field(default_factory=CrossReference)
