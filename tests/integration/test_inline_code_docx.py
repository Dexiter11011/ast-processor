"""Inline code integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.style_ids import CODE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_inline_code(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "inline-code.docx"
    convert_markdown_to_docx(fixtures_dir / "inline-code.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    p = root.find(f".//{{{W_NS}}}p")
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 3
    assert runs[0].find(f"{{{W_NS}}}t").text == "Run "
    code_run = runs[1]
    r_style = code_run.find(f".//{{{W_NS}}}rStyle")
    assert r_style is not None
    assert r_style.get(f"{{{W_NS}}}val") == CODE
    assert code_run.find(f".//{{{W_NS}}}rFonts") is None
    assert code_run.find(f"{{{W_NS}}}t").text == "npm install"
    assert runs[2].find(f"{{{W_NS}}}t").text == "."
