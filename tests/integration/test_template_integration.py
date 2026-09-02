"""Template merge and CLI integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md2docx.cli.main import main
from md2docx.ooxml.package import DocxPackageWriter
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.insertion import CONTENT_PLACEHOLDER
from md2docx.templates.reader import DocxPackageReader
from tests.helpers import read_docx_part


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "templates"


def test_template_merge_inserts_markdown_content(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("# Title\n\nBody paragraph.\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    template = DocxPackageReader.load(templates_dir / "minimal.docx")
    convert_markdown_to_docx(markdown, output, template=template)
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "Introduction" in document
    assert "Signature" in document
    assert CONTENT_PLACEHOLDER not in document
    assert "Title" in document
    assert "Body paragraph." in document


def test_corporate_template_preserves_header_footer(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Hello template.\n", encoding="utf-8")
    output = tmp_path / "corporate-out.docx"
    template = DocxPackageReader.load(templates_dir / "corporate.docx")
    convert_markdown_to_docx(markdown, output, template=template)
    with zipfile.ZipFile(output, "r") as zf:
        assert "word/header1.xml" in zf.namelist()
        assert "word/footer1.xml" in zf.namelist()
        header = zf.read("word/header1.xml").decode("utf-8")
        footer = zf.read("word/footer1.xml").decode("utf-8")
    assert "Company Name" in header
    assert "Confidential" in footer


def test_cli_template_flag(tmp_path: Path, templates_dir: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "hello-world.md"
    template = templates_dir / "minimal.docx"
    output = tmp_path / "hello.docx"
    code = main([str(markdown), "--template", str(template), "-o", str(output)])
    assert code == 0
    assert output.is_file()


def test_cli_missing_template_reports_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
):
    markdown = fixtures_dir / "hello-world.md"
    missing = tmp_path / "missing.docx"
    code = main([str(markdown), "--template", str(missing)])
    assert code == 2
    assert "template file not found" in capsys.readouterr().err


def test_cli_missing_placeholder_reports_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
    templates_dir: Path,
):
    parts = DocxPackageReader.load(templates_dir / "minimal.docx").copy_parts()
    document = read_docx_part(templates_dir / "minimal.docx", "word/document.xml").decode("utf-8")
    parts["word/document.xml"] = document.replace(CONTENT_PLACEHOLDER, "NO PLACEHOLDER").encode("utf-8")
    bad_template = tmp_path / "bad-template.docx"
    DocxPackageWriter().write_package(parts, bad_template)
    markdown = fixtures_dir / "hello-world.md"
    code = main([str(markdown), "--template", str(bad_template)])
    assert code == 2
    assert "insertion point" in capsys.readouterr().err
