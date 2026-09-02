"""Corporate navigation template integration test."""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

from md2docx.elements import create_default_registry
from md2docx.ooxml.package import DocxPackageWriter
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.templates.merger import TemplateMerger
from md2docx.templates.reader import DocxPackageReader
from md2docx.validation.package_validator import validate_docx_bytes
from tests.helpers import W_NS
from tests.navigation_fixtures import build_mixed_navigation_document


def _ensure_templates(templates_dir: Path) -> None:
    if (templates_dir / "corporate-navigation.docx").is_file():
        return
    script = Path(__file__).resolve().parents[2] / "scripts" / "build-template-fixtures.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent.parent)


def test_corporate_navigation_template_merge(tmp_path: Path, fixtures_dir: Path):
    templates_dir = fixtures_dir / "templates"
    _ensure_templates(templates_dir)
    template = DocxPackageReader.load(templates_dir / "corporate-navigation.docx")
    context = ProcessingContext.create_for_template(source_dir=fixtures_dir)
    processor = AstProcessor(create_default_registry())
    processor.process_document(build_mixed_navigation_document(), context)
    parts = TemplateMerger.merge(template, context)
    output = tmp_path / "corporate-navigation.docx"
    DocxPackageWriter().write_package(parts, output)

    with zipfile.ZipFile(output, "r") as zf:
        document_xml = zf.read("word/document.xml")
    root = etree.fromstring(document_xml)
    instr = [
        (node.text or "").strip()
        for node in root.findall(f".//{{{W_NS}}}instrText")
    ]
    assert any('TOC \\o "1-3"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Table"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok
