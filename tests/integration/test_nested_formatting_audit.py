"""Nested inline formatting audit."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def _run_flags(run: etree._Element) -> tuple[bool, bool]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    if r_pr is None:
        return False, False
    return r_pr.find(f"{{{W_NS}}}b") is not None, r_pr.find(f"{{{W_NS}}}i") is not None


def test_nested_formatting_patterns(tmp_path: Path):
    source = tmp_path / "nested.md"
    source.write_text(
        "\n".join(
            [
                "This is **bold and *italic*** text.",
                "",
                "This is *italic with **bold*** text.",
                "",
                "This is **bold with `inline code`**.",
                "",
                "This is [**bold link**](https://example.com).",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "nested.docx"
    convert_markdown_to_docx(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) >= 4

    p0_runs = paragraphs[0].findall(f"{{{W_NS}}}r")
    assert _run_flags(p0_runs[1]) == (True, False)
    assert _run_flags(p0_runs[2]) == (True, True)

    hyperlinks = root.findall(f".//{{{W_NS}}}hyperlink")
    assert hyperlinks
    assert hyperlinks[-1].get(f"{{{R_NS}}}id") is not None
