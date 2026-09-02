"""Raw metadata inputs before resolution."""

from __future__ import annotations

from dataclasses import dataclass

from md2docx.ast.metadata import DocumentMetadata
from md2docx.metadata.normalize import normalize_keywords, normalize_optional_string


@dataclass(frozen=True)
class CliMetadataInput:
    title: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    keywords: str | None = None


@dataclass(frozen=True)
class FrontMatterMetadata:
    title: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    keywords: tuple[str, ...] = ()

    @classmethod
    def from_raw(cls, raw: dict[str, str]) -> FrontMatterMetadata:
        keywords_raw = raw.get("keywords")
        if keywords_raw is not None:
            keywords = normalize_keywords(keywords_raw)
        else:
            keywords = ()
        return cls(
            title=normalize_optional_string(raw.get("title")),
            author=normalize_optional_string(raw.get("author")),
            date=normalize_optional_string(raw.get("date")),
            subject=normalize_optional_string(raw.get("subject")),
            keywords=keywords,
        )

    @classmethod
    def from_document_metadata(cls, metadata: DocumentMetadata) -> FrontMatterMetadata:
        return cls(
            title=normalize_optional_string(metadata.title or None),
            author=normalize_optional_string(metadata.author or None),
            date=normalize_optional_string(getattr(metadata, "date", None) or None),
            subject=normalize_optional_string(metadata.subject or None),
            keywords=normalize_keywords(metadata.keywords or None),
        )
