"""Integration tests for navigation layer."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_ast_to_docx
from md2docx.validation.package_validator import validate_docx_bytes
from tests.helpers import W_NS
from tests.navigation_fixtures import (
    build_list_of_figures_document,
    build_list_of_tables_document,
    build_mixed_navigation_document,
    build_toc_levels_document,
)


def _instr_texts(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    return [
        (node.text or "").strip()
        for node in root.findall(f".//{{{W_NS}}}instrText")
    ]


def test_toc_levels_field(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "toc-levels.docx"
    convert_ast_to_docx(build_toc_levels_document(), output, source_dir=fixtures_dir)
    instr = _instr_texts(output)
    assert any('TOC \\o "2-3"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok


def test_list_of_figures_field(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "lof.docx"
    convert_ast_to_docx(build_list_of_figures_document(), output, source_dir=fixtures_dir)
    instr = _instr_texts(output)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok


def test_list_of_tables_field(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "lot.docx"
    convert_ast_to_docx(build_list_of_tables_document(), output, source_dir=fixtures_dir)
    instr = _instr_texts(output)
    assert any('TOC \\h \\z \\c "Table"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok


def test_mixed_navigation_validates(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "mixed.docx"
    convert_ast_to_docx(build_mixed_navigation_document(), output, source_dir=fixtures_dir)
    instr = _instr_texts(output)
    assert any('TOC \\o "1-2"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Figure"' in text for text in instr)
    assert any('TOC \\h \\z \\c "Table"' in text for text in instr)
    assert validate_docx_bytes(output.read_bytes()).ok
