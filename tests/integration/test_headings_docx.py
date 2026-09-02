"""Headings integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _heading_paragraphs(docx_path: Path) -> list[tuple[str | None, str | None]]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    result: list[tuple[str | None, str | None]] = []
    for p in root.findall(f".//{{{W_NS}}}p"):
        p_pr = p.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            continue
        p_style = p_pr.find(f"{{{W_NS}}}pStyle")
        style = p_style.get(f"{{{W_NS}}}val") if p_style is not None else None
        t = p.find(f".//{{{W_NS}}}t")
        text = t.text if t is not None else None
        result.append((style, text))
    return result


def test_pipeline_headings(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "headings.docx"
    convert_markdown_to_docx(fixtures_dir / "headings.md", output_path)

    headings = _heading_paragraphs(output_path)
    assert headings == [
        ("Heading1", "Heading 1"),
        ("Heading2", "Heading 2"),
        ("Heading3", "Heading 3"),
    ]
