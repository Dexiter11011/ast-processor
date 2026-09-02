"""Integration tests for template navigation regions."""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.package import DocxPackageWriter
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.merger import TemplateMerger
from md2docx.templates.reader import DocxPackageReader
from md2docx.validation.package_validator import validate_docx_bytes
from md2docx.ooxml.xml_builder import w_tag
from tests.navigation_fixtures import build_mixed_navigation_document


def _ensure_templates(templates_dir: Path) -> None:
    required = (
        "regions-basic.docx",
        "regions-navigation.docx",
        "regions-complex.docx",
    )
    if all((templates_dir / name).is_file() for name in required):
        return
    script = Path(__file__).resolve().parents[2] / "scripts" / "build-template-fixtures.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent.parent)


def _field_instructions(document_xml: bytes) -> list[str]:
    root = etree.fromstring(document_xml)
    return [(node.text or "").strip() for node in root.findall(f".//{w_tag('instrText')}")]


def test_regions_navigation_template_deduplicates_markdown_directives(
    tmp_path: Path,
    fixtures_dir: Path,
):
    templates_dir = fixtures_dir / "templates"
    _ensure_templates(templates_dir)
    markdown = fixtures_dir / "markdown" / "navigation" / "mixed-navigation.md"
    if not markdown.is_file():
        markdown = tmp_path / "mixed.md"
        markdown.write_text(
            "<!-- toc -->\n<!-- lof -->\n<!-- lot -->\n\n# Introduction\n\nBody text.\n",
            encoding="utf-8",
        )
    output = tmp_path / "regions-navigation.docx"
    convert_markdown_to_docx(
        markdown,
        output,
        template=DocxPackageReader.load(templates_dir / "regions-navigation.docx"),
    )
    document_xml = zipfile.ZipFile(output).read("word/document.xml")
    instr = _field_instructions(document_xml)
    assert sum('TOC \\o "1-3"' in text for text in instr) == 1
    assert sum('TOC \\h \\z \\c "Figure"' in text for text in instr) == 1
    assert sum('TOC \\h \\z \\c "Table"' in text for text in instr) == 1
    assert validate_docx_bytes(output.read_bytes()).ok


def test_regions_basic_template_merge(tmp_path: Path, fixtures_dir: Path):
    from md2docx.elements import create_default_registry
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext

    templates_dir = fixtures_dir / "templates"
    _ensure_templates(templates_dir)
    template = DocxPackageReader.load(templates_dir / "regions-basic.docx")
    context = ProcessingContext.create_for_template(source_dir=fixtures_dir)
    processor = AstProcessor(create_default_registry())
    processor.process_document(build_mixed_navigation_document(), context)
    parts = TemplateMerger.merge(template, context)
    output = tmp_path / "regions-basic.docx"
    DocxPackageWriter().write_package(parts, output)

    document_xml = zipfile.ZipFile(output).read("word/document.xml")
    instr = _field_instructions(document_xml)
    assert any('TOC \\o "1-3"' in text for text in instr)
    assert "Introduction" in document_xml.decode("utf-8")
    assert validate_docx_bytes(output.read_bytes()).ok


def test_regions_complex_template_order(tmp_path: Path, fixtures_dir: Path):
    from md2docx.elements import create_default_registry
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext
    from md2docx.templates.context import DocumentContext

    templates_dir = fixtures_dir / "templates"
    _ensure_templates(templates_dir)
    template = DocxPackageReader.load(templates_dir / "regions-complex.docx")
    context = ProcessingContext.create_for_template(source_dir=fixtures_dir)
    processor = AstProcessor(create_default_registry())
    processor.process_document(build_mixed_navigation_document(), context)
    parts = TemplateMerger.merge(
        template,
        context,
        document_context=DocumentContext(title="Complex Regions"),
    )
    output = tmp_path / "regions-complex.docx"
    DocxPackageWriter().write_package(parts, output)

    root = etree.fromstring(zipfile.ZipFile(output).read("word/document.xml"))
    texts = [
        "".join((node.text or "") for node in paragraph.findall(f".//{w_tag('t')}"))
        for paragraph in root.findall(f".//{w_tag('body')}/{w_tag('p')}")
    ]
    assert texts[0] == "Title:"
    assert texts[1] == "Complex Regions"
    assert "Introduction" in texts
    assert texts.index("Introduction") < texts.index("Appendix navigation")
    assert validate_docx_bytes(output.read_bytes()).ok
