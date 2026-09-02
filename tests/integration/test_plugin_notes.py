"""Integration tests for the example notes plugin."""

from __future__ import annotations

import io
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.content_types import build_content_types_xml
from md2docx.ooxml.relationships import RelationshipManager
from md2docx.ooxml.styles import build_minimal_styles_xml
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.plugins.loader import load_plugins
from md2docx.templates.insertion import CONTENT_PLACEHOLDER
from md2docx.templates.reader import DocxPackageReader
from md2docx.validation.package_validator import validate_docx_bytes


def _notes_plugin_path() -> Path:
    return Path(__file__).resolve().parents[1] / "plugins" / "notes_plugin.py"


def test_note_directive_renders_styled_paragraph(tmp_path: Path):
    source = tmp_path / "note.md"
    source.write_text("<!-- note: Important -->\n\nBody paragraph.\n", encoding="utf-8")
    output = tmp_path / "note.docx"
    convert_markdown_to_docx(
        source,
        output,
        plugin_registry=load_plugins([_notes_plugin_path()]),
    )
    document_xml = zipfile.ZipFile(output).read("word/document.xml")
    assert b"Note:" in document_xml
    assert b"Important" in document_xml
    assert b"ExampleNote" in zipfile.ZipFile(output).read("word/styles.xml")
    assert validate_docx_bytes(output.read_bytes()).ok


def test_cli_plugin_loading(tmp_path: Path):
    source = tmp_path / "note.md"
    source.write_text("<!-- note: CLI -->\n", encoding="utf-8")
    output = tmp_path / "note.docx"
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "md2docx.cli.main",
            str(source),
            "--plugin",
            str(_notes_plugin_path()),
            "-o",
            str(output),
        ],
        cwd=str(root),
        env={"PYTHONPATH": str(root / "src"), **dict(__import__("os").environ)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    document_xml = zipfile.ZipFile(output).read("word/document.xml")
    assert b"Note:" in document_xml
    assert b"CLI" in document_xml


def test_invalid_plugin_reports_clear_error(tmp_path: Path):
    bad = tmp_path / "bad_plugin.py"
    bad.write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    source = tmp_path / "note.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "md2docx.cli.main",
            str(source),
            "--plugin",
            str(bad),
            "-o",
            str(output),
        ],
        cwd=str(root),
        env={"PYTHONPATH": str(root / "src"), **dict(__import__("os").environ)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Error:" in result.stderr
    assert "plugin" in result.stderr.lower()


def test_template_plugin_region(tmp_path: Path):
    rels = RelationshipManager()
    rels.add_styles_relationship()
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    body.append(api.paragraph([api.run("{{example_note}}")], style_id="Normal"))
    body.append(api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"))
    etree.SubElement(body, w_tag("sectPr"))
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    template_path = tmp_path / "plugin-region.docx"
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": serialize(root),
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    template_path.write_bytes(buf.getvalue())

    source = tmp_path / "content.md"
    source.write_text("<!-- note: In body -->\n\n# Title\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(
        source,
        output,
        template=DocxPackageReader.load(template_path),
        plugin_registry=load_plugins([_notes_plugin_path()]),
    )
    document_xml = zipfile.ZipFile(output).read("word/document.xml")
    assert b"Note:" in document_xml
    assert b"Template region" in document_xml
    assert b"In body" not in document_xml
