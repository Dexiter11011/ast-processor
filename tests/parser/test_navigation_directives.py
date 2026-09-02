"""Unit tests for caption/ref directive matchers."""

from __future__ import annotations

from md2docx.captions.kinds import CaptionKind
from md2docx.parser.block_directive import (
    match_caption_directive,
    match_lof_directive,
    match_lot_directive,
    match_ref_directive,
)


def test_lof_directive():
    assert match_lof_directive("<!-- lof -->")
    assert match_lof_directive("  <!-- LOF -->  ")


def test_lot_directive():
    assert match_lot_directive("<!-- lot -->")


def test_caption_directive_figure():
    result = match_caption_directive("<!-- caption: figure Architecture overview -->")
    assert result == (CaptionKind.FIGURE, "Architecture overview")


def test_caption_directive_table():
    result = match_caption_directive("<!-- caption: table Results -->")
    assert result == (CaptionKind.TABLE, "Results")


def test_ref_directive_with_prefix():
    result = match_ref_directive('<!-- ref: figure architecture prefix="See " -->')
    assert result == (CaptionKind.FIGURE, "architecture", "See ")


def test_ref_directive_default_prefix():
    result = match_ref_directive("<!-- ref: table results -->")
    assert result == (CaptionKind.TABLE, "results", "See ")


def test_non_directive_comment_not_matched():
    assert match_caption_directive("Some <!-- caption: figure X --> text") is None
    assert match_ref_directive("<!-- ref: figure -->") is None
