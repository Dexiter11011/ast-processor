"""Unit tests for caption bookmark naming."""

from __future__ import annotations

from md2docx.captions.kinds import CaptionKind
from md2docx.captions.naming import caption_bookmark_name


def test_figure_bookmark_name_from_caption_text():
    used: dict[str, int] = {}
    assert caption_bookmark_name(CaptionKind.FIGURE, "Architecture overview", used) == (
        "figure-architecture-overview"
    )


def test_table_bookmark_name_from_caption_text():
    used: dict[str, int] = {}
    assert caption_bookmark_name(CaptionKind.TABLE, "Configuration values", used) == (
        "table-configuration-values"
    )


def test_duplicate_caption_bookmarks_disambiguated():
    used: dict[str, int] = {}
    first = caption_bookmark_name(CaptionKind.FIGURE, "Architecture", used)
    second = caption_bookmark_name(CaptionKind.FIGURE, "Architecture", used)
    assert first == "figure-architecture"
    assert second == "figure-architecture-1"
