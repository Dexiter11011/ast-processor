"""Style system integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _p_style(p: etree._Element) -> str | None:
    p_pr = p.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    return p_style.get(f"{{{W_NS}}}val") if p_style is not None else None


def _run_flags(run: etree._Element) -> tuple[bool, bool]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    return bold, italic


def test_style_system_matrix(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "style-system-matrix.md"
    output = tmp_path / "style-system-matrix.docx"
    convert_markdown_to_docx(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p")
    assert _p_style(paragraphs[0]) == "Heading1"
    assert _p_style(paragraphs[1]) == "Normal"
    assert _p_style(paragraphs[2]) == "Quote"
    quote_runs = paragraphs[2].findall(f"{{{W_NS}}}r")
    assert _run_flags(quote_runs[0]) == (True, False)
    assert _p_style(paragraphs[3]) == "NoSpacing"
    assert _p_style(paragraphs[4]) == "ListParagraph"
    assert _p_style(paragraphs[6]) == "Heading1"
    heading_runs = paragraphs[6].findall(f"{{{W_NS}}}r")
    assert _run_flags(heading_runs[0]) == (True, False)
    assert _run_flags(heading_runs[1]) == (True, True)
