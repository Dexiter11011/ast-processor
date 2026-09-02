"""Bold integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _run_has_bold(run: etree._Element) -> bool:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    return r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None


def test_pipeline_bold(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "bold.docx"
    convert_markdown_to_docx(fixtures_dir / "bold.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    p = root.find(f".//{{{W_NS}}}p")
    assert p is not None
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 2
    assert not _run_has_bold(runs[0])
    assert runs[0].find(f"{{{W_NS}}}t").text == "Hello "
    assert _run_has_bold(runs[1])
    assert runs[1].find(f"{{{W_NS}}}t").text == "world"
