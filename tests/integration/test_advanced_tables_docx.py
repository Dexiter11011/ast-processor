"""Advanced table integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_advanced_tables(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "advanced-tables.docx"
    convert_markdown_to_docx(fixtures_dir / "advanced-tables.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    tables = root.findall(f".//{{{W_NS}}}tbl")
    assert len(tables) == 5

    shading_table = tables[0]
    fills = [shd.get(f"{{{W_NS}}}fill") for shd in shading_table.findall(f".//{{{W_NS}}}shd")]
    assert "FFF2CC" in fills
    assert "E2EFDA" in fills
    assert "DDEBF7" in fills

    centering_table = tables[1]
    valigns = [el.get(f"{{{W_NS}}}val") for el in centering_table.findall(f".//{{{W_NS}}}vAlign")]
    assert "center" in valigns
    jcs = [el.get(f"{{{W_NS}}}val") for el in centering_table.findall(f".//{{{W_NS}}}jc")]
    assert "center" in jcs

    horizontal_merge_table = tables[2]
    grid_spans = horizontal_merge_table.findall(f".//{{{W_NS}}}gridSpan")
    assert len(grid_spans) >= 1
    assert grid_spans[0].get(f"{{{W_NS}}}val") == "2"
    assert [t.text for t in horizontal_merge_table.findall(f".//{{{W_NS}}}t")][:5] == [
        "Region",
        "City",
        "Population",
        "Europe",
        "—",
    ]

    vertical_merge_table = tables[3]
    v_merges = vertical_merge_table.findall(f".//{{{W_NS}}}vMerge")
    assert len(v_merges) >= 2
    restart = [el for el in v_merges if el.get(f"{{{W_NS}}}val") != "continue"]
    continue_cells = [el for el in v_merges if el.get(f"{{{W_NS}}}val") == "continue"]
    assert len(restart) >= 1
    assert len(continue_cells) >= 2

    layout_table = tables[4]
    assert layout_table.find(f".//{{{W_NS}}}gridSpan") is not None
    assert layout_table.find(f".//{{{W_NS}}}shd") is not None
    assert [t.text for t in layout_table.findall(f".//{{{W_NS}}}t")][:3] == ["Section", "Metric", "Value"]

    all_text = " ".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "{bg:" not in all_text
    assert "^^" not in all_text
