"""Semantic and renderer equivalence between Markdown DSL and programmatic fixtures."""

from __future__ import annotations

import zipfile
from pathlib import Path

from md2docx.ast.types import Document, Image
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption, Figure, TableWithCaption
from md2docx.pipeline import convert_ast_to_docx, convert_markdown_to_docx
from tests.figures_fixtures import _simple_table
from tests.golden.xml_compare import assert_document_xml_equal


def _build_figure_equivalent() -> Document:
    return Document(
        children=[
            Figure(
                image=Image(src="logo.png", alt="Architecture"),
                caption=Caption(kind=CaptionKind.FIGURE, text="Architecture overview"),
            )
        ]
    )


def _build_table_equivalent() -> Document:
    return Document(
        children=[
            TableWithCaption(
                table=_simple_table(("Name", "Value"), ("A", "1")),
                caption=Caption(kind=CaptionKind.TABLE, text="Configuration values"),
            )
        ]
    )


def test_figure_dsl_matches_programmatic_document_xml(
    tmp_path: Path,
    fixtures_dir: Path,
):
    md_out = tmp_path / "figure-md.docx"
    prog_out = tmp_path / "figure-prog.docx"
    convert_markdown_to_docx(
        fixtures_dir / "markdown" / "navigation" / "figure.md",
        md_out,
    )
    convert_ast_to_docx(_build_figure_equivalent(), prog_out, source_dir=fixtures_dir)
    with zipfile.ZipFile(md_out) as md_zip, zipfile.ZipFile(prog_out) as prog_zip:
        assert_document_xml_equal(
            prog_zip.read("word/document.xml"),
            md_zip.read("word/document.xml"),
        )


def test_table_dsl_matches_programmatic_document_xml(
    tmp_path: Path,
    fixtures_dir: Path,
):
    md_out = tmp_path / "table-md.docx"
    prog_out = tmp_path / "table-prog.docx"
    convert_markdown_to_docx(
        fixtures_dir / "markdown" / "navigation" / "table-caption.md",
        md_out,
    )
    convert_ast_to_docx(_build_table_equivalent(), prog_out, source_dir=fixtures_dir)
    with zipfile.ZipFile(md_out) as md_zip, zipfile.ZipFile(prog_out) as prog_zip:
        assert_document_xml_equal(
            prog_zip.read("word/document.xml"),
            md_zip.read("word/document.xml"),
        )
