"""Ordered list restart tests — separate lists must not share numbering."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _ordered_list_num_ids(
    root: etree._Element,
    numbering_root: etree._Element,
    *,
    top_level_only: bool = False,
) -> list[str]:
    ordered_num_ids = {
        num.get(f"{{{W_NS}}}numId")
        for num in numbering_root.findall(f"{{{W_NS}}}num")
        if num.find(f"{{{W_NS}}}abstractNumId") is not None
        and num.find(f"{{{W_NS}}}abstractNumId").get(f"{{{W_NS}}}val") == "1"
    }
    ids: list[str] = []
    for p in root.iter(f"{{{W_NS}}}p"):
        p_pr = p.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            continue
        p_style = p_pr.find(f"{{{W_NS}}}pStyle")
        if p_style is None or p_style.get(f"{{{W_NS}}}val") != "ListParagraph":
            continue
        num_pr = p_pr.find(f"{{{W_NS}}}numPr")
        if num_pr is None:
            continue
        if top_level_only:
            ilvl = num_pr.find(f"{{{W_NS}}}ilvl")
            level = ilvl.get(f"{{{W_NS}}}val") if ilvl is not None else "0"
            if level != "0":
                continue
        num_id = num_pr.find(f"{{{W_NS}}}numId")
        if num_id is None:
            continue
        value = num_id.get(f"{{{W_NS}}}val")
        if value in ordered_num_ids:
            ids.append(value)
    return ids


def _list_num_ids(root: etree._Element) -> list[str]:
    ids: list[str] = []
    for p in root.iter(f"{{{W_NS}}}p"):
        p_pr = p.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            continue
        p_style = p_pr.find(f"{{{W_NS}}}pStyle")
        if p_style is None or p_style.get(f"{{{W_NS}}}val") != "ListParagraph":
            continue
        num_pr = p_pr.find(f"{{{W_NS}}}numPr")
        if num_pr is None:
            continue
        num_id = num_pr.find(f"{{{W_NS}}}numId")
        assert num_id is not None
        ids.append(num_id.get(f"{{{W_NS}}}val"))
    return ids


def test_separate_ordered_lists_get_distinct_num_ids(tmp_path: Path):
    source = "1. Alpha\n2. Beta\n\nPlain paragraph.\n\n1. Gamma\n2. Delta"
    input_path = tmp_path / "two-lists.md"
    output_path = tmp_path / "two-lists.docx"
    input_path.write_text(source, encoding="utf-8")
    convert_markdown_to_docx(input_path, output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        numbering = etree.fromstring(zf.read("word/numbering.xml"))

    num_ids = _list_num_ids(root)
    assert num_ids == ["3", "3", "4", "4"]

    for num in numbering.findall(f"{{{W_NS}}}num"):
        num_id = num.get(f"{{{W_NS}}}numId")
        if num_id not in {"3", "4"}:
            continue
        override = num.find(f"{{{W_NS}}}lvlOverride")
        assert override is not None
        start = override.find(f"{{{W_NS}}}startOverride")
        assert start is not None
        assert start.get(f"{{{W_NS}}}val") == "1"


def test_integration_article_top_level_ordered_lists_restart(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "integration-article.docx"
    convert_markdown_to_docx(fixtures_dir / "integration-article.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        numbering = etree.fromstring(zf.read("word/numbering.xml"))

    num_ids = _ordered_list_num_ids(root, numbering, top_level_only=True)
    # Section 3 (4), Section 4.1 checklist (3), Section 6 themes (4), References (5), Appendix B (3)
    assert len(num_ids) == 19
    assert len(set(num_ids)) == 5
    blocks = [
        (4, num_ids[0]),
        (3, num_ids[4]),
        (4, num_ids[7]),
        (5, num_ids[11]),
        (3, num_ids[16]),
    ]
    offset = 0
    for length, expected_id in blocks:
        assert num_ids[offset : offset + length] == [expected_id] * length
        offset += length
    assert num_ids[0] != num_ids[4] != num_ids[7] != num_ids[11] != num_ids[16]
