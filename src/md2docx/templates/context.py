"""Document-level data for template placeholders and core properties."""

from __future__ import annotations

from dataclasses import dataclass


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@dataclass(frozen=True)
class DocumentContext:
    """User/document data separate from renderer infrastructure."""

    title: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    keywords: str | None = None

    def get(self, name: str) -> str | None:
        """Return a scalar value by placeholder name."""
        field = getattr(self, name, None)
        if field is None or not isinstance(field, str):
            return None
        return field

    def has_core_props_values(self) -> bool:
        return any(
            value
            for value in (self.title, self.author, self.subject, self.keywords)
        )

    def has_values(self) -> bool:
        return self.has_core_props_values() or self.date is not None
