"""Golden tests for template placeholder document output."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.context import DocumentContext
from md2docx.templates.reader import DocxPackageReader
from tests.golden.xml_compare import assert_document_xml_equal, pretty_xml
from tests.helpers import read_docx_part

GOLDEN_CASES = (
    "template_placeholders_basic",
    "template_placeholders_formatting",
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


def _build_document_xml(
    case: str,
    fixtures_dir: Path,
    output_path: Path,
) -> bytes:
    templates_dir = fixtures_dir / "templates"
    markdown = fixtures_dir / "hello-world.md"
    if case == "template_placeholders_basic":
        template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
        context = DocumentContext(
            title="Project Documentation",
            author="John Doe",
            date="2026-08-31",
        )
    elif case == "template_placeholders_formatting":
        template = DocxPackageReader.load(templates_dir / "placeholders-formatting.docx")
        context = DocumentContext(title="Project Documentation", author="John Doe")
    else:
        raise AssertionError(f"unknown golden case: {case}")

    convert_markdown_to_docx(
        markdown,
        output_path,
        template=template,
        document_context=context,
    )
    return read_docx_part(output_path, "word/document.xml")


@pytest.mark.parametrize("case", GOLDEN_CASES)
def test_template_document_xml_matches_golden(
    case: str,
    fixtures_dir: Path,
    expected_dir: Path,
    tmp_path: Path,
    update_golden: bool,
):
    expected_path = expected_dir / f"{case}.document.xml"
    actual = _build_document_xml(case, fixtures_dir, tmp_path / f"{case}.docx")

    if update_golden:
        expected_dir.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(pretty_xml(actual), encoding="utf-8")
        pytest.skip(f"updated golden file {expected_path.name}")

    assert expected_path.is_file(), (
        f"missing golden file {expected_path.name}; run with UPDATE_GOLDEN=1"
    )
    assert_document_xml_equal(expected_path.read_bytes(), actual)
