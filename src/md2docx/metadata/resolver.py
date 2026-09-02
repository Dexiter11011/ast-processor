"""Resolve document metadata from multiple sources."""

from __future__ import annotations

from md2docx.metadata.normalize import normalize_date, normalize_keywords, normalize_optional_string
from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.metadata.sources import CliMetadataInput, FrontMatterMetadata


def _pick(
    cli_value: str | None,
    front_matter_value: str | None,
    *,
    default: str | None = None,
) -> str | None:
    if cli_value is not None:
        return normalize_optional_string(cli_value)
    if front_matter_value is not None:
        return normalize_optional_string(front_matter_value)
    return normalize_optional_string(default)


def _pick_keywords(
    cli_value: str | None,
    front_matter_value: tuple[str, ...],
) -> tuple[str, ...]:
    if cli_value is not None:
        return normalize_keywords(cli_value)
    return front_matter_value


class MetadataResolver:
    """Resolve metadata with deterministic per-field precedence."""

    @staticmethod
    def resolve(
        *,
        cli: CliMetadataInput | None = None,
        front_matter: FrontMatterMetadata | None = None,
        defaults: ResolvedDocumentMetadata | None = None,
    ) -> ResolvedDocumentMetadata:
        cli_input = cli or CliMetadataInput()
        fm = front_matter or FrontMatterMetadata()
        base = defaults or ResolvedDocumentMetadata()

        date_cli = normalize_date(cli_input.date, field="date") if cli_input.date is not None else None
        date_fm = normalize_date(fm.date, field="date") if fm.date is not None else None

        return ResolvedDocumentMetadata(
            title=_pick(cli_input.title, fm.title, default=base.title),
            author=_pick(cli_input.author, fm.author, default=base.author),
            date=date_cli if cli_input.date is not None else date_fm or base.date,
            subject=_pick(cli_input.subject, fm.subject, default=base.subject),
            keywords=_pick_keywords(cli_input.keywords, fm.keywords or base.keywords),
            created=base.created,
            modified=base.modified,
        )


def resolve_document_metadata(
    *,
    cli: CliMetadataInput | None = None,
    front_matter: FrontMatterMetadata | None = None,
    defaults: ResolvedDocumentMetadata | None = None,
) -> ResolvedDocumentMetadata:
    return MetadataResolver.resolve(cli=cli, front_matter=front_matter, defaults=defaults)
