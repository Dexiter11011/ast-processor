"""Blockquote integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _paragraph_style(p: etree._Element) -> str | None:
    p_pr = p.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    if p_style is None:
        return None
    return p_style.get(f"{{{W_NS}}}val")


def test_pipeline_blockquote(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "blockquote.docx"
    convert_markdown_to_docx(fixtures_dir / "blockquote.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 2
    assert [p.find(f".//{{{W_NS}}}t").text for p in paragraphs] == ["Quote line one.", "Quote line two."]
    assert all(_paragraph_style(p) == "Quote" for p in paragraphs)
