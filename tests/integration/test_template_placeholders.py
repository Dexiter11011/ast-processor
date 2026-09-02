"""Integration tests for template placeholders."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md2docx.cli.main import main
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.context import DocumentContext
from md2docx.templates.insertion import CONTENT_PLACEHOLDER
from md2docx.templates.reader import DocxPackageReader
from tests.helpers import read_docx_part


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "templates"


def test_placeholders_basic_template_merge(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("# Markdown Title\n\nBody paragraph.\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
    convert_markdown_to_docx(
        markdown,
        output,
        template=template,
        document_context=DocumentContext(
            title="Project Documentation",
            author="John Doe",
            date="2026-08-31",
        ),
    )
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "Project Documentation" in document
    assert "John Doe" in document
    assert "2026-08-31" in document
    assert "Body paragraph." in document
    assert CONTENT_PLACEHOLDER not in document
    assert "{{title}}" not in document


def test_cli_placeholder_flags(tmp_path: Path, templates_dir: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "hello-world.md"
    template = templates_dir / "placeholders-basic.docx"
    output = tmp_path / "hello.docx"
    code = main(
        [
            str(markdown),
            "--template",
            str(template),
            "--title",
            "Project Documentation",
            "--author",
            "John Doe",
            "--date",
            "2026-08-31",
            "-o",
            str(output),
        ]
    )
    assert code == 0
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "Project Documentation" in document
    assert "John Doe" in document


def test_cli_missing_placeholder_value_reports_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
    templates_dir: Path,
):
    markdown = fixtures_dir / "hello-world.md"
    template = templates_dir / "placeholders-basic.docx"
    code = main([str(markdown), "--template", str(template)])
    assert code == 2
    assert "missing value for template placeholder" in capsys.readouterr().err


def test_template_metadata_writes_core_props(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Body\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
    convert_markdown_to_docx(
        markdown,
        output,
        template=template,
        document_context=DocumentContext(
            title="Project Documentation",
            author="John Doe",
            date="2026-08-31",
        ),
    )
    with zipfile.ZipFile(output, "r") as zf:
        core = etree.fromstring(zf.read("docProps/core.xml"))
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        assert core.find("dc:title", ns).text == "Project Documentation"
        assert core.find("dc:creator", ns).text == "John Doe"


def test_special_characters_in_placeholder_values(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Body\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
    convert_markdown_to_docx(
        markdown,
        output,
        template=template,
        document_context=DocumentContext(
            title="A & B <Draft>",
            author="Иван Иванов",
            date="2026-08-31",
        ),
    )
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "A &amp; B &lt;Draft&gt;" in document
    assert "Иван Иванов" in document
