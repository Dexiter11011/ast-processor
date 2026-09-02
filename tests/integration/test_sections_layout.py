"""Page break integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS


def test_page_break_emits_break_element(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "page-break.docx"
    convert_markdown_to_docx(fixtures_dir / "page-break.md", output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    breaks = root.findall(f".//{{{W_NS}}}br")
    assert any(br.get(f"{{{W_NS}}}type") == "page" for br in breaks)


def test_landscape_section(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "landscape.docx"
    convert_markdown_to_docx(fixtures_dir / "landscape.md", output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    sect_props = root.findall(f".//{{{W_NS}}}sectPr")
    assert len(sect_props) >= 2
    landscape = [
        sp
        for sp in sect_props
        if (pg := sp.find(f"{{{W_NS}}}pgSz")) is not None
        and pg.get(f"{{{W_NS}}}orient") == "landscape"
    ]
    assert landscape


def test_header_footer_parts(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "header-footer.docx"
    convert_markdown_to_docx(fixtures_dir / "header-footer.md", output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()

    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
        assert "word/header1.xml" in names
        assert "word/footer1.xml" in names
        root = etree.fromstring(zf.read("word/document.xml"))

    header_ref = root.find(f".//{{{W_NS}}}headerReference")
    footer_ref = root.find(f".//{{{W_NS}}}footerReference")
    assert header_ref is not None
    assert footer_ref is not None


def test_sections_integration(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "sections-integration.docx"
    convert_markdown_to_docx(fixtures_dir / "sections-integration.md", output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        assert "word/numbering.xml" in zf.namelist()

    assert root.find(f".//{{{W_NS}}}tbl") is not None
    assert root.find(f".//{{{W_NS}}}br") is not None
    assert len(root.findall(f".//{{{W_NS}}}sectPr")) >= 2
