"""Italic integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _run_has_italic(run: etree._Element) -> bool:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    return r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None


def test_pipeline_italic(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "italic.docx"
    convert_markdown_to_docx(fixtures_dir / "italic.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    p = root.find(f".//{{{W_NS}}}p")
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 2
    assert not _run_has_italic(runs[0])
    assert runs[0].find(f"{{{W_NS}}}t").text == "Hello "
    assert _run_has_italic(runs[1])
    assert runs[1].find(f"{{{W_NS}}}t").text == "world"
