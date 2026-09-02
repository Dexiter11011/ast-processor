"""Template integration for Markdown navigation DSL."""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.reader import DocxPackageReader
from md2docx.validation.package_validator import validate_docx_bytes
from tests.helpers import W_NS


def _ensure_templates(templates_dir: Path) -> None:
    if (templates_dir / "corporate-navigation.docx").is_file():
        return
    script = Path(__file__).resolve().parents[2] / "scripts" / "build-template-fixtures.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent.parent)


def test_navigation_dsl_with_corporate_template(tmp_path: Path, fixtures_dir: Path):
    templates_dir = fixtures_dir / "templates"
    _ensure_templates(templates_dir)
    fixture = fixtures_dir / "markdown" / "navigation" / "mixed-navigation.md"
    output = tmp_path / "template-nav.docx"
    template = DocxPackageReader.load(templates_dir / "corporate-navigation.docx")
    convert_markdown_to_docx(fixture, output, template=template)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    instr = [
        (node.text or "").strip()
        for node in root.findall(f".//{{{W_NS}}}instrText")
    ]
    assert any('TOC \\o "1-3"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok
