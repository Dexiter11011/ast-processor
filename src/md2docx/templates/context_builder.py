"""Build DocumentContext values from CLI and front matter sources."""

from __future__ import annotations

from md2docx.ast.metadata import DocumentMetadata
from md2docx.metadata.resolver import resolve_document_metadata
from md2docx.metadata.sources import CliMetadataInput, FrontMatterMetadata
from md2docx.templates.context import DocumentContext


def build_document_context(
    *,
    cli_title: str | None = None,
    cli_author: str | None = None,
    cli_date: str | None = None,
    cli_subject: str | None = None,
    cli_keywords: str | None = None,
    front_matter: DocumentMetadata | FrontMatterMetadata | None = None,
) -> DocumentContext:
    """Build document context with CLI values overriding front matter."""
    if isinstance(front_matter, DocumentMetadata):
        fm = FrontMatterMetadata.from_document_metadata(front_matter)
    elif front_matter is not None:
        fm = front_matter
    else:
        fm = FrontMatterMetadata()

    resolved = resolve_document_metadata(
        cli=CliMetadataInput(
            title=cli_title,
            author=cli_author,
            date=cli_date,
            subject=cli_subject,
            keywords=cli_keywords,
        ),
        front_matter=fm,
    )
    return resolved_to_document_context(resolved)


def resolved_to_document_context(resolved) -> DocumentContext:
    from md2docx.metadata.resolved import ResolvedDocumentMetadata

    if not isinstance(resolved, ResolvedDocumentMetadata):
        raise TypeError("expected ResolvedDocumentMetadata")
    return DocumentContext(
        title=resolved.title,
        author=resolved.author,
        date=resolved.date,
        subject=resolved.subject,
        keywords=resolved.keywords_display,
    )


def document_context_to_metadata(context: DocumentContext) -> DocumentMetadata:
    """Map document context to legacy metadata for core properties builders."""
    from md2docx.metadata.resolved import ResolvedDocumentMetadata

    resolved = ResolvedDocumentMetadata(
        title=context.title,
        author=context.author,
        date=context.date,
        subject=context.subject,
        keywords=tuple(
            part.strip()
            for part in (context.keywords or "").split(",")
            if part.strip()
        ),
    )
    return resolved.to_document_metadata()
