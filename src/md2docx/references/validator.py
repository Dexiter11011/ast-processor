"""Reference validation helpers for conversion and package checks."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.references.manager import BookmarkManager


@dataclass
class ReferenceValidationReport:
    """Collected reference issues during document generation."""

    broken_internal_links: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.broken_internal_links


def validate_bookmark_manager(manager: BookmarkManager) -> ReferenceValidationReport:
    """Build a report from bookmark manager state after conversion."""
    return ReferenceValidationReport(
        broken_internal_links=sorted(manager.broken_targets),
    )
