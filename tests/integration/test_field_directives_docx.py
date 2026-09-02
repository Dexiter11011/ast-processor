"""Tests for body field directives."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.parser.block_directive import match_field_directive
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_match_field_directive():
    assert match_field_directive("<!-- field: date -->") == ("date", "")
    assert match_field_directive("<!-- field: ref architecture -->") == ("ref", "architecture")
    assert match_field_directive("<!-- field: seq Figure -->") == ("seq", "Figure")
    assert match_field_directive("<!-- toc -->") is None


def test_fields_all_fixture(tmp_path: Path, fixtures_dir: Path):
    markdown = fixtures_dir / "fields-all.md"
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(markdown, output)
    with zipfile.ZipFile(output, "r") as zf:
        header = etree.fromstring(zf.read("word/header1.xml"))
        document = etree.fromstring(zf.read("word/document.xml"))
    header_fields = header.findall(f".//{{{W_NS}}}fldSimple")
    header_instructions = {field.get(f"{{{W_NS}}}instr") for field in header_fields}
    assert " TITLE " in header_instructions
    assert " AUTHOR " in header_instructions
    assert " DATE " in header_instructions
    assert len(header.findall(f".//{{{W_NS}}}p")) == 3

    body_simple = document.findall(f".//{{{W_NS}}}fldSimple")
    simple_instructions = {field.get(f"{{{W_NS}}}instr") for field in body_simple}
    assert " DATE " in simple_instructions

    body_instr = document.findall(f".//{{{W_NS}}}instrText")
    body_text = " ".join((node.text or "") for node in body_instr)
    assert "REF ref-target" in body_text
    assert "SEQ Figure" in body_text
