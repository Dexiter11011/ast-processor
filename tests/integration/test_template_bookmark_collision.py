"""Template bookmark collision integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_ast_to_docx
from md2docx.templates.merger import TemplateMerger
from md2docx.templates.reader import DocxPackageReader
from md2docx.processor.context import ProcessingContext
from md2docx.ooxml.package import DocxPackageWriter
from md2docx.validation.package_validator import validate_docx_bytes
from tests.helpers import W_NS
from tests.navigation_fixtures import build_bookmark_collision_document


def _bookmark_names(document_xml: bytes) -> list[str]:
    root = etree.fromstring(document_xml)
    return [
        node.get(f"{{{W_NS}}}name")
        for node in root.findall(f".//{{{W_NS}}}bookmarkStart")
        if node.get(f"{{{W_NS}}}name")
    ]


def _ref_targets(document_xml: bytes) -> list[str]:
    root = etree.fromstring(document_xml)
    targets: list[str] = []
    for node in root.findall(f".//{{{W_NS}}}instrText"):
        text = (node.text or "").strip()
        if text.upper().startswith("REF "):
            parts = text.split()
            if len(parts) >= 2:
                targets.append(parts[1])
    return targets


def test_template_bookmark_collision_remaps_generated_content(
    tmp_path: Path,
    fixtures_dir: Path,
):
    templates_dir = fixtures_dir / "templates"
    template_path = templates_dir / "navigation-collision.docx"
    if not template_path.is_file():
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[2] / "scripts" / "build-template-fixtures.py"
        subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent.parent)

    template = DocxPackageReader.load(template_path)
    context = ProcessingContext.create_for_template(source_dir=fixtures_dir)
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.elements import create_default_registry

    processor = AstProcessor(create_default_registry())
    processor.process_document(build_bookmark_collision_document(), context)
    parts = TemplateMerger.merge(template, context)
    output = tmp_path / "collision.docx"
    DocxPackageWriter().write_package(parts, output)

    with zipfile.ZipFile(output, "r") as zf:
        document_xml = zf.read("word/document.xml")

    names = _bookmark_names(document_xml)
    assert "architecture" in names
    assert "architecture-1" in names
    assert "figure-architecture" in names
    assert "figure-architecture-1" in names
    assert "table-results" in names
    assert "table-results-1" in names

    ref_targets = _ref_targets(document_xml)
    assert "architecture-1" in ref_targets
    assert "figure-architecture-1" in ref_targets
    assert "table-results-1" in ref_targets

    report = validate_docx_bytes(output.read_bytes())
    assert report.ok, report.messages
