"""Table variants integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_table_variants(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "table-variants.docx"
    convert_markdown_to_docx(fixtures_dir / "table-variants.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    tables = root.findall(f".//{{{W_NS}}}tbl")
    assert len(tables) == 4

    assert [t.text for t in tables[0].findall(f".//{{{W_NS}}}t")] == ["Name", "Age", "Bob", "20", "Ann", "30"]
    header_p = tables[0].find(f".//{{{W_NS}}}tc").find(f"{{{W_NS}}}p")
    assert header_p.find(f".//{{{W_NS}}}b") is not None

    alignments = [jc.get(f"{{{W_NS}}}val") for jc in tables[1].findall(f".//{{{W_NS}}}jc")]
    assert alignments[:3] == ["left", "center", "right"]

    none_borders = tables[2].find(f".//{{{W_NS}}}tblBorders").find(f"{{{W_NS}}}top")
    assert none_borders.get(f"{{{W_NS}}}val") == "nil"

    double_borders = tables[3].find(f".//{{{W_NS}}}tblBorders").find(f"{{{W_NS}}}top")
    assert double_borders.get(f"{{{W_NS}}}val") == "double"

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    content_children = [c for c in body if c.tag != f"{{{W_NS}}}sectPr"]
    assert [child.tag.split("}")[-1] for child in content_children] == ["tbl", "p", "tbl", "p", "tbl", "p", "tbl", "p"]

    all_text = " ".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "table:" not in all_text
    assert "<!--" not in all_text
