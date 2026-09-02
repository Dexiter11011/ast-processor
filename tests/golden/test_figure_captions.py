"""Golden tests for figure/table caption XML output."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from md2docx.pipeline import convert_ast_to_docx
from tests.figures_fixtures import build_interleaved_figures_tables_document, build_single_figure_document
from tests.golden.xml_compare import assert_document_xml_equal, pretty_xml

GOLDEN_CASES = (
    "figure-caption",
    "interleaved-sequences",
)


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "expected"


@pytest.fixture
def update_golden(request: pytest.FixtureRequest) -> bool:
    if request.config.getoption("--update-golden", default=False):
        return True
    return os.environ.get("UPDATE_GOLDEN", "").lower() in {"1", "true", "yes"}


@pytest.mark.parametrize("case", GOLDEN_CASES)
def test_caption_document_xml_matches_golden(
    case: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    if case == "figure-caption":
        document = build_single_figure_document()
    else:
        document = build_interleaved_figures_tables_document()
    output = tmp_path / f"{case}.docx"
    convert_ast_to_docx(document, output, source_dir=fixtures_dir)
    with zipfile.ZipFile(output, "r") as zf:
        actual = zf.read("word/document.xml")
    expected_path = expected_dir / f"{case}.document.xml"
    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"updated golden file {expected_path.name}")
    assert expected_path.is_file(), f"missing golden file {expected_path.name}"
    assert_document_xml_equal(expected_path.read_bytes(), actual)
