"""Nested inline integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.style_ids import CODE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _run_flags(run: etree._Element) -> tuple[bool, bool, str | None]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    r_style = r_pr.find(f"{{{W_NS}}}rStyle") if r_pr is not None else None
    style_val = r_style.get(f"{{{W_NS}}}val") if r_style is not None else None
    return bold, italic, style_val


def test_pipeline_nested_inline(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "nested-inline.docx"
    convert_markdown_to_docx(fixtures_dir / "nested-inline.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    runs = root.find(f".//{{{W_NS}}}p").findall(f"{{{W_NS}}}r")
    assert len(runs) == 6
    assert runs[0].find(f"{{{W_NS}}}t").text == "This is "
    assert _run_flags(runs[1]) == (True, False, None)
    assert runs[1].find(f"{{{W_NS}}}t").text == "bold, "
    assert _run_flags(runs[2]) == (True, True, None)
    assert runs[2].find(f"{{{W_NS}}}t").text == "italic"
    assert _run_flags(runs[3]) == (True, False, None)
    assert runs[3].find(f"{{{W_NS}}}t").text == ", and "
    assert _run_flags(runs[4]) == (True, False, CODE)
    assert runs[4].find(f"{{{W_NS}}}t").text == "code"
    assert _run_flags(runs[5]) == (False, False, None)
    assert runs[5].find(f"{{{W_NS}}}t").text == "."
