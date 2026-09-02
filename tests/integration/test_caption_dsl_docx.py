"""Integration tests for Markdown caption/navigation DSL."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation.package_validator import validate_docx_bytes
from tests.helpers import W_NS


def _instr_texts(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    return [
        (node.text or "").strip()
        for node in root.findall(f".//{{{W_NS}}}instrText")
    ]


def _bookmark_names(docx_path: Path) -> set[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    return {
        node.get(f"{{{W_NS}}}name")
        for node in root.findall(f".//{{{W_NS}}}bookmarkStart")
        if node.get(f"{{{W_NS}}}name")
    }


def test_figure_dsl_renders_seq_and_bookmark(tmp_path: Path, fixtures_dir: Path):
    fixture = fixtures_dir / "markdown" / "navigation" / "figure.md"
    output = tmp_path / "figure.docx"
    convert_markdown_to_docx(fixture, output)
    instr = " ".join(_instr_texts(output))
    assert "SEQ Figure" in instr
    names = _bookmark_names(output)
    assert "figure-architecture-overview" in names
    assert validate_docx_bytes(output.read_bytes()).ok


def test_table_caption_dsl_renders_seq_and_bookmark(tmp_path: Path, fixtures_dir: Path):
    fixture = fixtures_dir / "markdown" / "navigation" / "table-caption.md"
    output = tmp_path / "table.docx"
    convert_markdown_to_docx(fixture, output)
    instr = " ".join(_instr_texts(output))
    assert "SEQ Table" in instr
    assert "table-configuration-values" in _bookmark_names(output)
    assert validate_docx_bytes(output.read_bytes()).ok


def test_mixed_navigation_dsl_fields(tmp_path: Path, fixtures_dir: Path):
    fixture = fixtures_dir / "markdown" / "navigation" / "mixed-navigation.md"
    output = tmp_path / "mixed.docx"
    convert_markdown_to_docx(fixture, output)
    instr = _instr_texts(output)
    assert any('TOC \\o "1-2"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Table"' in text for text in instr)
    assert any("REF figure-architecture-overview" in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok


def test_forward_reference_before_figure(tmp_path: Path, fixtures_dir: Path):
    fixture = fixtures_dir / "markdown" / "navigation" / "forward-reference.md"
    output = tmp_path / "forward.docx"
    convert_markdown_to_docx(fixture, output)
    assert validate_docx_bytes(output.read_bytes()).ok
