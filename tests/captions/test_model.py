"""Unit tests for caption semantic model."""

from __future__ import annotations

from md2docx.captions.kinds import CaptionKind, SequenceKind
from md2docx.captions.model import Caption, Figure
from md2docx.ast.types import Image


def test_caption_has_no_number_field():
    caption = Caption(kind=CaptionKind.FIGURE, text="Architecture")
    assert caption.text == "Architecture"
    assert not hasattr(caption, "number")


def test_sequence_kind_maps_from_caption_kind():
    assert SequenceKind.from_caption_kind(CaptionKind.FIGURE) is SequenceKind.FIGURE
    assert SequenceKind.from_caption_kind(CaptionKind.TABLE) is SequenceKind.TABLE


def test_figure_wraps_image_and_caption():
    figure = Figure(
        image=Image(src="logo.png"),
        caption=Caption(kind=CaptionKind.FIGURE, text="Overview"),
    )
    assert figure.type == "figure"
    assert figure.caption is not None
    assert figure.caption.kind is CaptionKind.FIGURE
