"""Lists + tables + inline formatting integration test."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS


def _p_style(p: etree._Element) -> str | None:
    p_pr = p.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    return p_style.get(f"{{{W_NS}}}val") if p_style is not None else None


def test_lists_tables_integration(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "lists-tables-integration.md"
    output = tmp_path / "lists-tables-integration.docx"
    convert_markdown_to_docx(source, output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        assert "word/numbering.xml" in zf.namelist()

    paragraphs = root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p")
    assert _p_style(paragraphs[0]) == "Heading1"
    assert _p_style(paragraphs[1]) == "Normal"

    list_items = [p for p in paragraphs if _p_style(p) == "ListParagraph"]
    assert len(list_items) >= 5

    tbl = root.find(f".//{{{W_NS}}}tbl")
    assert tbl is not None
    tbl_style = tbl.find(f".//{{{W_NS}}}tblStyle")
    assert tbl_style is not None
    assert tbl_style.get(f"{{{W_NS}}}val") == "TableGrid"

    header_row = tbl.findall(f"{{{W_NS}}}tr")[0]
    assert header_row.find(f".//{{{W_NS}}}tblHeader") is not None

    bold = tbl.find(f".//{{{W_NS}}}rPr/{{{W_NS}}}b")
    assert bold is not None

    hyperlinks = root.findall(f".//{{{W_NS}}}hyperlink")
    assert hyperlinks

    assert _p_style(paragraphs[-1]) == "Quote"
