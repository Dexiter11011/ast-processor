"""Unit tests for caption transform coalescing."""

from __future__ import annotations

import pytest

from md2docx.ast.types import Document, Image, Table, TableCell, TableRow, Paragraph, Text
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Figure, TableWithCaption
from md2docx.parser.caption_marker import CaptionMarker
from md2docx.parser.caption_transform import apply_caption_transform, normalize_ref_target
from md2docx.parser.errors import CaptionParseError
from md2docx.parser.ref_marker import RefMarker


def _simple_table() -> Table:
    cell = TableCell(children=[Paragraph(children=[Text(value="A")])])
    return Table(rows=[TableRow(cells=[cell], header=True)])


def test_image_and_figure_caption_marker_become_figure():
    document = Document(
        children=[
            Image(src="logo.png", alt=""),
            CaptionMarker(kind=CaptionKind.FIGURE, text="Architecture"),
        ]
    )
    result = apply_caption_transform(document)
    assert len(result.children) == 1
    node = result.children[0]
    assert isinstance(node, Figure)
    assert node.image.src == "logo.png"
    assert node.caption is not None
    assert node.caption.text == "Architecture"


def test_plain_image_remains_image():
    document = Document(children=[Image(src="logo.png", alt="")])
    result = apply_caption_transform(document)
    assert isinstance(result.children[0], Image)


def test_table_caption_marker_before_table_becomes_table_with_caption():
    document = Document(
        children=[
            CaptionMarker(kind=CaptionKind.TABLE, text="Results"),
            _simple_table(),
        ]
    )
    result = apply_caption_transform(document)
    assert len(result.children) == 1
    assert isinstance(result.children[0], TableWithCaption)


def test_orphan_caption_marker_raises():
    document = Document(children=[CaptionMarker(kind=CaptionKind.FIGURE, text="X", line=3)])
    with pytest.raises(CaptionParseError, match="figure caption directive must immediately follow an image"):
        apply_caption_transform(document, source_path="doc.md")


def test_ref_marker_becomes_cross_reference_block():
    document = Document(
        children=[
            RefMarker(kind=CaptionKind.FIGURE, slug="architecture-overview", prefix="See "),
        ]
    )
    result = apply_caption_transform(document)
    assert result.children[0].type == "cross_reference"
    assert result.children[0].reference.target == "figure-architecture-overview"


def test_normalize_ref_target_adds_prefix():
    assert normalize_ref_target(CaptionKind.FIGURE, "architecture") == "figure-architecture"
    assert normalize_ref_target(CaptionKind.FIGURE, "figure-architecture") == "figure-architecture"
