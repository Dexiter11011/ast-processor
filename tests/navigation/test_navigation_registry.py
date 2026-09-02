"""Unit tests for NavigationRegistry."""

from __future__ import annotations

from md2docx.navigation.kinds import NavigationTargetKind
from md2docx.navigation.registry import NavigationRegistry


def test_registry_preserves_document_order():
    registry = NavigationRegistry()
    registry.register_heading(bookmark_name="intro", label="Introduction", level=1)
    registry.register_figure(bookmark_name="figure-a", label="Figure")
    registry.register_table(bookmark_name="table-a", label="Table")
    registry.register_figure(bookmark_name="figure-b", label="Figure")

    kinds = [target.kind for target in registry.targets]
    assert kinds == [
        NavigationTargetKind.HEADING,
        NavigationTargetKind.FIGURE,
        NavigationTargetKind.TABLE,
        NavigationTargetKind.FIGURE,
    ]


def test_targets_of_kind_filters_figures():
    registry = NavigationRegistry()
    registry.register_figure(bookmark_name="figure-a", label="Figure")
    registry.register_table(bookmark_name="table-a", label="Table")
    registry.register_figure(bookmark_name="figure-b", label="Figure")

    figures = registry.targets_of_kind(NavigationTargetKind.FIGURE)
    assert [target.bookmark_name for target in figures] == ["figure-a", "figure-b"]
