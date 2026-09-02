"""Ordered list integration tests."""

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


def test_pipeline_ordered_list(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "ordered-list.docx"
    convert_markdown_to_docx(fixtures_dir / "ordered-list.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        numbering = zf.read("word/numbering.xml").decode("utf-8")
        root = etree.fromstring(zf.read("word/document.xml"))

    assert "decimal" in numbering
    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 3
    assert [p.find(f".//{{{W_NS}}}t").text for p in paragraphs] == ["First", "Second", "Third"]
    for p in paragraphs:
        assert _paragraph_style(p) == "ListParagraph"


def test_bullet_and_ordered_use_different_list_styles(tmp_path: Path):
    source = "- Bullet\n\n1. First\n2. Second"
    input_path = tmp_path / "mixed.md"
    output_path = tmp_path / "mixed.docx"
    input_path.write_text(source, encoding="utf-8")
    convert_markdown_to_docx(input_path, output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        numbering = zf.read("word/numbering.xml").decode("utf-8")
        root = etree.fromstring(zf.read("word/document.xml"))

    assert "decimal" in numbering
    assert "bullet" in numbering
    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 4
    styles = [_paragraph_style(p) for p in paragraphs]
    assert styles == ["ListParagraph", "Normal", "ListParagraph", "ListParagraph"]
