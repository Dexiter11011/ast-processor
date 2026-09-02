"""Metadata resolver unit tests."""

from __future__ import annotations

import pytest

from md2docx.metadata.errors import MetadataValidationError
from md2docx.metadata.resolver import resolve_document_metadata
from md2docx.metadata.sources import CliMetadataInput, FrontMatterMetadata


def test_cli_overrides_front_matter_per_field():
    resolved = resolve_document_metadata(
        cli=CliMetadataInput(title="CLI Title"),
        front_matter=FrontMatterMetadata(
            title="FM Title",
            author="FM Author",
            date="2026-08-31",
            subject="FM Subject",
            keywords=("markdown", "docx"),
        ),
    )
    assert resolved.title == "CLI Title"
    assert resolved.author == "FM Author"
    assert resolved.date == "2026-08-31"
    assert resolved.subject == "FM Subject"
    assert resolved.keywords == ("markdown", "docx")


def test_cli_subject_and_keywords_override_front_matter():
    resolved = resolve_document_metadata(
        cli=CliMetadataInput(subject="CLI Subject", keywords="a, b"),
        front_matter=FrontMatterMetadata(subject="FM Subject", keywords=("x",)),
    )
    assert resolved.subject == "CLI Subject"
    assert resolved.keywords == ("a", "b")


def test_cli_date_overrides_front_matter_date():
    resolved = resolve_document_metadata(
        cli=CliMetadataInput(date="2026-09-01"),
        front_matter=FrontMatterMetadata(date="2026-08-31"),
    )
    assert resolved.date == "2026-09-01"


def test_front_matter_date_used_when_cli_missing():
    resolved = resolve_document_metadata(
        front_matter=FrontMatterMetadata(date="2026-08-31"),
    )
    assert resolved.date == "2026-08-31"


def test_empty_strings_normalize_to_none():
    resolved = resolve_document_metadata(
        cli=CliMetadataInput(title="  ", author=""),
        front_matter=FrontMatterMetadata(title="FM Title"),
    )
    assert resolved.title is None
    assert resolved.author is None


def test_invalid_cli_date_raises():
    with pytest.raises(MetadataValidationError) as exc:
        resolve_document_metadata(cli=CliMetadataInput(date="not-a-date"))
    assert exc.value.field == "date"


def test_datetime_front_matter_normalized_to_date():
    resolved = resolve_document_metadata(
        front_matter=FrontMatterMetadata(date="2026-08-31T12:30:00"),
    )
    assert resolved.date == "2026-08-31"


def test_keywords_comma_separated():
    resolved = resolve_document_metadata(
        front_matter=FrontMatterMetadata(keywords=("a", "b", "c")),
    )
    assert resolved.keywords == ("a", "b", "c")
    assert resolved.keywords_display == "a, b, c"
