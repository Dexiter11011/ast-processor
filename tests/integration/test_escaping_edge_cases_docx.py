"""Escaping edge-case integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_escaping_edge_cases(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "escaping-edge-cases.docx"
    convert_markdown_to_docx(fixtures_dir / "escaping-edge-cases.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    paragraphs = [c for c in body if c.tag == f"{{{W_NS}}}p"]
    texts = ["".join(t.text or "" for t in p.findall(f".//{{{W_NS}}}t")) for p in paragraphs]
    assert texts == [
        "*",
        "**",
        "_",
        "__",
        "[",
        "]",
        "(",
        ")",
        "<",
        ">",
        "&",
        "Привет мир",
        "日本語",
        "😀",
    ]
