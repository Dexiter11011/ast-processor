"""Inline formatting matrix integration test."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.style_ids import CODE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def _run_flags(run: etree._Element) -> tuple[bool, bool, str | None]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    r_style = r_pr.find(f"{{{W_NS}}}rStyle") if r_pr is not None else None
    style_val = r_style.get(f"{{{W_NS}}}val") if r_style is not None else None
    return bold, italic, style_val


def _paragraph_text(p: etree._Element) -> str:
    return "".join(t.text or "" for t in p.findall(f".//{{{W_NS}}}t"))


def test_inline_formatting_matrix(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "inline-formatting-matrix.md"
    output = tmp_path / "inline-formatting-matrix.docx"
    convert_markdown_to_docx(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p")
    texts = [_paragraph_text(p) for p in paragraphs]

    assert texts[1] == "Bold only"
    bold_only = paragraphs[1].findall(f"{{{W_NS}}}r")
    assert len(bold_only) == 1
    assert _run_flags(bold_only[0]) == (True, False, None)

    assert texts[2] == "Italic only"
    italic_only = paragraphs[2].findall(f"{{{W_NS}}}r")
    assert _run_flags(italic_only[0]) == (False, True, None)

    nested = paragraphs[4].findall(f"{{{W_NS}}}r")
    assert _run_flags(nested[1]) == (True, True, None)

    code_para = paragraphs[6].findall(f"{{{W_NS}}}r")
    assert _run_flags(code_para[0]) == (False, False, CODE)

    bold_code = paragraphs[7].findall(f"{{{W_NS}}}r")
    assert _run_flags(bold_code[1]) == (True, False, CODE)

    hello_world = paragraphs[12].findall(f"{{{W_NS}}}r")
    assert len(hello_world) == 3
    assert _run_flags(hello_world[0]) == (True, False, None)
    assert _run_flags(hello_world[1]) == (False, False, None)
    assert _run_flags(hello_world[2]) == (True, False, None)

    hyperlinks = root.findall(f".//{{{W_NS}}}hyperlink")
    assert len(hyperlinks) >= 4
    for link in hyperlinks:
        assert link.get(f"{{{R_NS}}}id") is not None
