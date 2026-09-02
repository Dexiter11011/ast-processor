"""Horizontal rule integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_horizontal_rule(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "horizontal-rule.docx"
    convert_markdown_to_docx(fixtures_dir / "horizontal-rule.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 1
    p_pr = paragraphs[0].find(f"{{{W_NS}}}pPr")
    assert p_pr is not None
    p_bdr = p_pr.find(f"{{{W_NS}}}pBdr")
    assert p_bdr is not None
    bottom = p_bdr.find(f"{{{W_NS}}}bottom")
    assert bottom is not None
    assert bottom.get(f"{{{W_NS}}}val") == "single"
