"""Golden tests for GFM fixture document.xml snapshots."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from tests.golden.xml_compare import assert_document_xml_equal, pretty_xml
from tests.helpers import read_docx_part

GFM_GOLDEN_CASES = (
    ("gfm-task-list", "markdown/gfm/task-list.md"),
    ("gfm-strikethrough", "markdown/gfm/strikethrough.md"),
    ("gfm-autolinks", "markdown/gfm/autolinks.md"),
    ("gfm-hard-breaks", "markdown/gfm/hard-breaks.md"),
    ("gfm-escaped-markdown", "markdown/gfm/escaped-markdown.md"),
    ("gfm-unicode", "markdown/gfm/unicode-gfm.md"),
    ("gfm-nested", "markdown/gfm/nested-gfm.md"),
    ("gfm-integration", "gfm-integration.md"),
)


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "expected"


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def update_golden(request: pytest.FixtureRequest) -> bool:
    if request.config.getoption("--update-golden", default=False):
        return True
    return os.environ.get("UPDATE_GOLDEN", "").lower() in {"1", "true", "yes"}


@pytest.mark.parametrize("case,relative_md", GFM_GOLDEN_CASES)
def test_gfm_document_xml_matches_golden(
    case: str,
    relative_md: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    fixture = fixtures_dir / relative_md
    expected_path = expected_dir / f"{case}.document.xml"
    assert fixture.is_file(), f"missing fixture {fixture}"

    convert_markdown_to_docx(fixture, tmp_path / f"{case}.docx")
    actual = read_docx_part(tmp_path / f"{case}.docx", "word/document.xml")

    if update_golden or not expected_path.is_file():
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"golden updated for {case}")

    assert_document_xml_equal(expected_path.read_bytes(), actual)
