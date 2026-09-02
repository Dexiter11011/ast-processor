"""Table integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_table(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "table.docx"
    convert_markdown_to_docx(fixtures_dir / "table.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    tables = root.findall(f".//{{{W_NS}}}tbl")
    assert len(tables) == 1
    texts = [t.text for t in tables[0].findall(f".//{{{W_NS}}}t")]
    assert texts == ["Name", "Age", "Bob", "20", "Ann", "30"]
    assert len(tables[0].findall(f".//{{{W_NS}}}tr")) == 3
    assert len(tables[0].findall(f".//{{{W_NS}}}tc")) == 6
