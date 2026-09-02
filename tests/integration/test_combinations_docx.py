"""Nested bold+italic integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _run_flags(run: etree._Element) -> tuple[bool, bool]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    return bold, italic


def test_pipeline_bold_and_italic(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "combinations.docx"
    convert_markdown_to_docx(fixtures_dir / "combinations.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    p = root.find(f".//{{{W_NS}}}p")
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 4

    assert runs[0].find(f"{{{W_NS}}}t").text == "This is "
    assert _run_flags(runs[0]) == (False, False)

    assert runs[1].find(f"{{{W_NS}}}t").text == "bold and "
    assert _run_flags(runs[1]) == (True, False)

    assert runs[2].find(f"{{{W_NS}}}t").text == "italic"
    assert _run_flags(runs[2]) == (True, True)

    assert runs[3].find(f"{{{W_NS}}}t").text == "."
    assert _run_flags(runs[3]) == (False, False)
