"""Nested list integration tests."""

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


def _list_ilvl(p: etree._Element) -> str | None:
    if _paragraph_style(p) != "ListParagraph":
        return None
    p_pr = p.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return "0"
    num_pr = p_pr.find(f"{{{W_NS}}}numPr")
    if num_pr is None:
        return "0"
    ilvl = num_pr.find(f"{{{W_NS}}}ilvl")
    return ilvl.get(f"{{{W_NS}}}val") if ilvl is not None else "0"


def test_pipeline_nested_list(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "nested-list.docx"
    convert_markdown_to_docx(fixtures_dir / "nested-list.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        numbering = zf.read("word/numbering.xml").decode("utf-8")
        root = etree.fromstring(zf.read("word/document.xml"))

    assert "multilevel" in numbering
    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 4
    assert [p.find(f".//{{{W_NS}}}t").text for p in paragraphs] == ["One", "Nested A", "Nested B", "Two"]
    assert [_list_ilvl(p) for p in paragraphs] == ["0", "1", "1", "0"]
    for p in paragraphs:
        assert _paragraph_style(p) == "ListParagraph"
