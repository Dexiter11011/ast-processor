"""Validate navigation registry state before package generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.navigation.registry import NavigationRegistry
from md2docx.references.manager import BookmarkManager


@dataclass
class NavigationValidationReport:
    """Collected navigation validation issues."""

    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_navigation(
    navigation: NavigationRegistry,
    bookmarks: BookmarkManager,
) -> NavigationValidationReport:
    """Ensure every navigation target has a matching bookmark anchor."""
    report = NavigationValidationReport()
    seen_names: set[str] = set()
    for target in navigation.targets:
        if target.bookmark_name in seen_names:
            report.errors.append(
                f'duplicate navigation bookmark name "{target.bookmark_name}"'
            )
        seen_names.add(target.bookmark_name)
        if bookmarks.resolve(target.bookmark_name) is None:
            report.errors.append(
                f'navigation target "{target.bookmark_name}" has no bookmark anchor'
            )
    return report
