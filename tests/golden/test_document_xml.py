"""Golden tests: compare generated word/document.xml against expected snapshots."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from tests.golden.xml_compare import assert_document_xml_equal, pretty_xml
from tests.helpers import read_docx_part

GOLDEN_CASES = (
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
    "external-links",
    "internal-links",
    "bookmarks",
    "duplicate-heading-bookmarks",
    "toc",
    "toc-levels",
    "links-and-toc",
    "references-integration",
)


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "expected"


@pytest.fixture
def update_golden(request: pytest.FixtureRequest) -> bool:
    if request.config.getoption("--update-golden", default=False):
        return True
    return os.environ.get("UPDATE_GOLDEN", "").lower() in {"1", "true", "yes"}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate tests/expected/*.document.xml from fixtures",
    )


def _build_document_xml(markdown_path: Path, output_path: Path) -> bytes:
    convert_markdown_to_docx(markdown_path, output_path)
    return read_docx_part(output_path, "word/document.xml")


@pytest.mark.parametrize("case", GOLDEN_CASES)
def test_document_xml_matches_golden(
    case: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    fixture = fixtures_dir / f"{case}.md"
    expected_path = expected_dir / f"{case}.document.xml"
    assert fixture.is_file(), f"missing fixture {fixture}"

    actual = _build_document_xml(fixture, tmp_path / f"{case}.docx")

    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"updated golden file {expected_path.name}")

    assert expected_path.is_file(), (
        f"missing golden file {expected_path.name}; "
        f"run: python scripts/update-golden.py"
    )
    expected = expected_path.read_bytes()
    assert_document_xml_equal(expected, actual)
