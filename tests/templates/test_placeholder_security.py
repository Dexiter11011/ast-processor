"""Security tests for template placeholders."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.context import DocumentContext
from md2docx.templates.reader import DocxPackageReader
from tests.helpers import read_docx_part


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "templates"


def test_scalar_values_do_not_inject_raw_xml(tmp_path: Path, templates_dir: Path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Body\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
    convert_markdown_to_docx(
        markdown,
        output,
        template=template,
        document_context=DocumentContext(
            title='</w:t><w:t>injected',
            author="Safe Author",
            date="2026-08-31",
        ),
    )
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "</w:t><w:t>injected" not in document
    assert "&lt;/w:t&gt;&lt;w:t&gt;injected" in document
