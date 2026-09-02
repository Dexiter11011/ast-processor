"""Golden tests for word/numbering.xml on list fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from tests.golden.xml_compare import assert_document_xml_equal
from tests.helpers import read_docx_part

LIST_CASES = (
    "unordered-list",
    "ordered-list",
    "nested-list",
)


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "expected"


@pytest.mark.parametrize("case", LIST_CASES)
def test_numbering_xml_matches_golden(case: str, fixtures_dir: Path, expected_dir: Path, tmp_path: Path):
    fixture = fixtures_dir / f"{case}.md"
    expected_path = expected_dir / f"{case}.numbering.xml"
    output = tmp_path / f"{case}.docx"
    convert_markdown_to_docx(fixture, output)

    actual = read_docx_part(output, "word/numbering.xml")
    assert expected_path.is_file(), f"missing golden {expected_path.name}"
    assert_document_xml_equal(expected_path.read_bytes(), actual)
