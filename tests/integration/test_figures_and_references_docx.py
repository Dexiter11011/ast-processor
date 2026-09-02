"""Integration tests for figures, captions, sequences, and cross-references."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_ast_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS
from tests.figures_fixtures import (
    build_interleaved_figures_tables_document,
    build_single_figure_document,
    build_single_table_document,
)


def _instr_text(document_root: etree._Element) -> str:
    return " ".join(
        (node.text or "")
        for node in document_root.findall(f".//{{{W_NS}}}instrText")
    )


def test_single_figure_caption_emits_seq_and_bookmark(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "figure.docx"
    convert_ast_to_docx(build_single_figure_document(), output, source_dir=fixtures_dir)
    report = validate_docx(output)
    assert report.ok, report.format_messages()
    with zipfile.ZipFile(output, "r") as zf:
        document = etree.fromstring(zf.read("word/document.xml"))
    instr = _instr_text(document)
    assert "SEQ Figure" in instr
    assert document.find(f".//{{{W_NS}}}bookmarkStart[@{{{W_NS}}}name='figure-architecture']") is not None
    caption_style = document.findall(f".//{{{W_NS}}}pStyle")
    assert any(el.get(f"{{{W_NS}}}val") == "Caption" for el in caption_style)


def test_single_table_caption_emits_seq_table(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "table.docx"
    convert_ast_to_docx(build_single_table_document(), output, source_dir=fixtures_dir)
    with zipfile.ZipFile(output, "r") as zf:
        document = etree.fromstring(zf.read("word/document.xml"))
    instr = _instr_text(document)
    assert "SEQ Table" in instr
    assert document.find(f".//{{{W_NS}}}bookmarkStart[@{{{W_NS}}}name='table-results']") is not None


def test_interleaved_sequences_and_refs(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "interleaved.docx"
    convert_ast_to_docx(
        build_interleaved_figures_tables_document(),
        output,
        source_dir=fixtures_dir,
    )
    report = validate_docx(output)
    assert report.ok, report.format_messages()
    with zipfile.ZipFile(output, "r") as zf:
        document = etree.fromstring(zf.read("word/document.xml"))
    instr = _instr_text(document)
    assert instr.count("SEQ Figure") == 3
    assert instr.count("SEQ Table") == 2
    assert "REF figure-architecture-overview" in instr
    assert "REF table-configuration-values" in instr
    assert "REF figure-deployment-topology" in instr
    assert "\\r" in instr


def test_no_static_figure_numbers_in_body(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "no-static.docx"
    convert_ast_to_docx(build_interleaved_figures_tables_document(), output, source_dir=fixtures_dir)
    with zipfile.ZipFile(output, "r") as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    assert "Figure 1" not in xml
    assert "Table 1" not in xml
