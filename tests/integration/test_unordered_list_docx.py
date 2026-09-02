"""Unordered list integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import NUMBERING_REL_TYPE
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


def test_pipeline_unordered_list(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "unordered-list.docx"
    convert_markdown_to_docx(fixtures_dir / "unordered-list.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        names = zf.namelist()
        assert "word/numbering.xml" in names
        numbering = zf.read("word/numbering.xml").decode("utf-8")
        root = etree.fromstring(zf.read("word/document.xml"))
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")

    assert NUMBERING_REL_TYPE in rels
    assert "multilevel" in numbering
    assert "bullet" in numbering
    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 3
    texts = [p.find(f".//{{{W_NS}}}t").text for p in paragraphs]
    assert texts == ["One", "Two", "Three"]
    for p in paragraphs:
        assert _paragraph_style(p) == "ListParagraph"
