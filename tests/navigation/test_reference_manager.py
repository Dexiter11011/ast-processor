"""Unit tests for ReferenceManager typed validation."""

from __future__ import annotations

import pytest

from md2docx.captions.kinds import CaptionKind
from md2docx.fields.errors import MissingRefTargetError
from md2docx.navigation.errors import ReferenceKindMismatchError
from md2docx.navigation.reference import ReferenceManager
from md2docx.navigation.registry import NavigationRegistry
from md2docx.references.manager import BookmarkManager


def _setup() -> ReferenceManager:
    bookmarks = BookmarkManager()
    navigation = NavigationRegistry()
    bookmarks.register("figure-a", bookmark_id=0)
    navigation.register_figure(bookmark_name="figure-a", label="Figure")
    bookmarks.register("table-a", bookmark_id=1)
    navigation.register_table(bookmark_name="table-a", label="Table")
    return ReferenceManager(navigation=navigation, bookmarks=bookmarks)


def test_resolve_figure_ref():
    refs = _setup()
    assert refs.resolve_bookmark_for_ref("figure-a", CaptionKind.FIGURE) == "figure-a"


def test_reject_table_target_for_figure_ref():
    refs = _setup()
    with pytest.raises(ReferenceKindMismatchError, match="not a figure target"):
        refs.resolve_bookmark_for_ref("table-a", CaptionKind.FIGURE)


def test_reject_missing_target():
    refs = _setup()
    with pytest.raises(MissingRefTargetError):
        refs.resolve_bookmark_for_ref("missing", CaptionKind.FIGURE)
