"""Validate every fixture DOCX through the package validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx

FIXTURE_NAMES = (
    "empty",
    "hello-world",
    "multiple-paragraphs",
    "headings",
    "bold",
    "italic",
    "combinations",
    "inline-code",
    "link",
    "unordered-list",
    "ordered-list",
    "nested-list",
    "blockquote",
    "horizontal-rule",
    "code-block",
    "xml-escaping",
    "image",
    "table",
    "table-variants",
    "advanced-tables",
    "nested-inline",
    "escaping-edge-cases",
    "document-metadata",
    "page-break",
    "landscape",
    "header-footer",
    "sections-integration",
    "integration-article",
    "all-iterations",
)


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_fixture_docx_passes_package_validation(
    fixture_name: str,
    fixtures_dir: Path,
    tmp_path: Path,
):
    """Markdown → DOCX → validate package, XML, relationships, references."""
    source = fixtures_dir / f"{fixture_name}.md"
    output = tmp_path / f"{fixture_name}.docx"
    convert_markdown_to_docx(source, output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()
