"""Golden tests for dynamic field XML output."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from tests.golden.xml_compare import assert_document_xml_equal, pretty_xml
from tests.helpers import read_docx_part

GOLDEN_CASES = (
    "footer-page-numbers",
    "fields-header-footer",
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
        help="Regenerate tests/expected/*.footer.xml from fixtures",
    )


@pytest.mark.parametrize("case", GOLDEN_CASES)
def test_footer_xml_matches_golden(
    case: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    markdown = fixtures_dir / f"{case}.md"
    output = tmp_path / f"{case}.docx"
    convert_markdown_to_docx(markdown, output)
    actual = read_docx_part(output, "word/footer1.xml")
    expected_path = expected_dir / f"{case}.footer.xml"
    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"updated golden file {expected_path.name}")
    assert expected_path.is_file(), f"missing golden file {expected_path.name}"
    assert_document_xml_equal(expected_path.read_bytes(), actual)


@pytest.mark.parametrize("case", ("footer-page-numbers",))
def test_settings_xml_matches_golden(
    case: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    markdown = fixtures_dir / f"{case}.md"
    output = tmp_path / f"{case}.docx"
    convert_markdown_to_docx(markdown, output)
    with zipfile.ZipFile(output, "r") as zf:
        actual = zf.read("word/settings.xml")
    expected_path = expected_dir / f"{case}.settings.xml"
    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"updated golden file {expected_path.name}")
    assert expected_path.is_file(), f"missing golden file {expected_path.name}"
    assert_document_xml_equal(expected_path.read_bytes(), actual)
