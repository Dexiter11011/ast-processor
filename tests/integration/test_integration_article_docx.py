"""Integration article fixture — full pipeline smoke test."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS


def _list_paragraph_count(root: etree._Element) -> int:
    count = 0
    for p in root.iter(f"{{{W_NS}}}p"):
        p_pr = p.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            continue
        p_style = p_pr.find(f"{{{W_NS}}}pStyle")
        if p_style is not None and p_style.get(f"{{{W_NS}}}val") == "ListParagraph":
            count += 1
    return count


def test_integration_article_docx(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "integration-article.docx"
    convert_markdown_to_docx(fixtures_dir / "integration-article.md", output_path)
    report = validate_docx(output_path)
    assert report.ok, report.format_messages()

    with zipfile.ZipFile(output_path, "r") as zf:
        core = zf.read("docProps/core.xml").decode("utf-8")
        root = etree.fromstring(zf.read("word/document.xml"))
        media = [name for name in zf.namelist() if name.startswith("word/media/")]
        assert "word/numbering.xml" in zf.namelist()

    assert "Global Renewable Power Capacity in 2024" in core
    assert "IRENA" in core
    assert len(root.findall(f".//{{{W_NS}}}tbl")) == 12
    assert len(root.findall(f".//{{{W_NS}}}tblHeader")) >= 2
    assert len(root.findall(f".//{{{W_NS}}}tblStyle")) >= 1
    assert _list_paragraph_count(root) >= 60
    assert len(media) == 3
    assert root.find(f".//{{{W_NS}}}pStyle") is not None
    assert root.find(f".//{{{W_NS}}}hyperlink") is not None

    list_styles = {
        p_style.get(f"{{{W_NS}}}val")
        for p in root.iter(f"{{{W_NS}}}p")
        if (p_pr := p.find(f"{{{W_NS}}}pPr")) is not None
        and (p_style := p_pr.find(f"{{{W_NS}}}pStyle")) is not None
        and (num_pr := p_pr.find(f"{{{W_NS}}}numPr")) is not None
    }
    assert list_styles == {"ListParagraph"}
