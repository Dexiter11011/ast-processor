"""Unit tests for DocumentContext."""

from __future__ import annotations

import pytest

from md2docx.ast.metadata import DocumentMetadata
from md2docx.templates.context import DocumentContext
from md2docx.templates.context_builder import build_document_context, document_context_to_metadata


def test_empty_context_has_no_values():
    context = DocumentContext()
    assert not context.has_values()
    assert not context.has_core_props_values()


def test_full_context_is_immutable():
    context = DocumentContext(title="Title", author="Author", date="2026-08-31")
    with pytest.raises(AttributeError):
        context.title = "Other"  # type: ignore[misc]


def test_cli_overrides_front_matter():
    front_matter = DocumentMetadata(title="FM Title", author="FM Author")
    context = build_document_context(
        cli_title="CLI Title",
        cli_author="CLI Author",
        cli_date="2026-08-31",
        cli_subject="CLI Subject",
        cli_keywords="a, b",
        front_matter=front_matter,
    )
    assert context.title == "CLI Title"
    assert context.author == "CLI Author"
    assert context.date == "2026-08-31"
    assert context.subject == "CLI Subject"
    assert context.keywords == "a, b"


def test_front_matter_used_when_cli_missing():
    front_matter = DocumentMetadata(title="FM Title", author="FM Author", subject="Subj")
    context = build_document_context(front_matter=front_matter)
    assert context.title == "FM Title"
    assert context.author == "FM Author"
    assert context.subject == "Subj"


def test_get_returns_scalar_values():
    context = DocumentContext(title="A & B <Draft>", author="Иван Иванов")
    assert context.get("title") == "A & B <Draft>"
    assert context.get("author") == "Иван Иванов"
    assert context.get("missing") is None


def test_to_metadata_maps_core_fields():
    context = DocumentContext(title="T", author="A", subject="S", keywords="K")
    metadata = document_context_to_metadata(context)
    assert metadata.title == "T"
    assert metadata.author == "A"
    assert metadata.subject == "S"
    assert metadata.keywords == "K"
