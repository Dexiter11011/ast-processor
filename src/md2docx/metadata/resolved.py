"""Canonical resolved document metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from md2docx.ast.metadata import DocumentMetadata


@dataclass(frozen=True)
class ResolvedDocumentMetadata:
    """Single source of truth for document metadata after precedence resolution."""

    title: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    keywords: tuple[str, ...] = ()
    created: datetime | None = None
    modified: datetime | None = None

    @property
    def keywords_display(self) -> str | None:
        if not self.keywords:
            return None
        return ", ".join(self.keywords)

    def has_core_props_values(self) -> bool:
        return any(
            value
            for value in (self.title, self.author, self.subject, self.keywords)
        )

    def has_values(self) -> bool:
        return self.has_core_props_values() or self.date is not None

    def to_document_metadata(self) -> DocumentMetadata:
        """Legacy bridge for core properties builder during migration."""
        return DocumentMetadata(
            title=self.title or "",
            author=self.author or "",
            subject=self.subject or "",
            keywords=self.keywords_display or "",
            date=self.date or "",
        )
