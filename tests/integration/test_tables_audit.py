"""Table structure audit."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS


def test_table_rows_cells_and_inline_bold(tmp_path: Path):
    source = tmp_path / "table.md"
    source.write_text(
        "| Name | Description |\n|------|-------------|\n| Bob  | **Developer** |\n",
        encoding="utf-8",
    )
    output = tmp_path / "table.docx"
    convert_markdown_to_docx(source, output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    rows = root.findall(f".//{{{W_NS}}}tr")
    assert len(rows) == 2
    assert len(rows[0].findall(f"{{{W_NS}}}tc")) == 2
    bold = root.find(f".//{{{W_NS}}}rPr/{{{W_NS}}}b")
    assert bold is not None
    texts = [t.text for t in root.findall(f".//{{{W_NS}}}t")]
    assert "Developer" in texts
