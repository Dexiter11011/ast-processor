"""Integration tests for dynamic fields."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import read_docx_part, W_NS


def test_footer_page_numbers_fixture(tmp_path: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "footer-page-numbers.md"
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(markdown, output)
    with zipfile.ZipFile(output, "r") as zf:
        footer = etree.fromstring(zf.read("word/footer1.xml"))
        settings = etree.fromstring(zf.read("word/settings.xml"))
    page_fields = footer.findall(f".//{{{W_NS}}}fldSimple")
    assert len(page_fields) == 2
    instructions = {field.get(f"{{{W_NS}}}instr") for field in page_fields}
    assert " PAGE " in instructions
    assert " NUMPAGES " in instructions
    assert settings.find(f".//{{{W_NS}}}updateFields") is not None


def test_header_footer_fields_fixture(tmp_path: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "fields-header-footer.md"
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(markdown, output)
    with zipfile.ZipFile(output, "r") as zf:
        header = etree.fromstring(zf.read("word/header1.xml"))
        footer = etree.fromstring(zf.read("word/footer1.xml"))
    assert header.find(f".//{{{W_NS}}}fldSimple") is not None
    assert len(footer.findall(f".//{{{W_NS}}}fldSimple")) == 2


def test_header_title_and_author_fields_combined(tmp_path: Path, fixtures_dir: Path):
    """Multiple header directives append paragraphs into one header part."""
    markdown = fixtures_dir / "fields-header-title-author.md"
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(markdown, output)
    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
        assert "word/header1.xml" in names
        assert "word/header2.xml" not in names
        header = etree.fromstring(zf.read("word/header1.xml"))
        document = etree.fromstring(zf.read("word/document.xml"))
        rels = etree.fromstring(zf.read("word/_rels/document.xml.rels"))
    fields = header.findall(f".//{{{W_NS}}}fldSimple")
    instructions = {field.get(f"{{{W_NS}}}instr") for field in fields}
    assert " TITLE " in instructions
    assert " AUTHOR " in instructions
    assert len(header.findall(f".//{{{W_NS}}}p")) == 2
    header_ref = document.find(f".//{{{W_NS}}}headerReference")
    assert header_ref is not None
    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    rid = header_ref.get(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )
    target = rels.find(f".//{{{rel_ns}}}Relationship[@Id='{rid}']")
    assert target is not None
    assert target.get("Target") == "header1.xml"


def test_no_update_fields_flag(tmp_path: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "footer-page-numbers.md"
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(markdown, output, update_fields=False)
    with zipfile.ZipFile(output, "r") as zf:
        assert "word/settings.xml" not in zf.namelist()
