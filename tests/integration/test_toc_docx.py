"""TOC field integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _toc_field_paragraphs(root: etree._Element) -> list[etree._Element]:
    paragraphs = []
    for para in root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p"):
        instr = para.find(f".//{{{W_NS}}}instrText")
        if instr is not None and "TOC" in (instr.text or ""):
            paragraphs.append(para)
    return paragraphs


def test_simple_toc_field(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "toc.docx"
    convert_markdown_to_docx(fixtures_dir / "toc.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    toc_paras = _toc_field_paragraphs(root)
    assert len(toc_paras) == 1
    instr = toc_paras[0].find(f".//{{{W_NS}}}instrText")
    assert 'TOC \\o "1-3"' in (instr.text or "")


def test_toc_levels(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "toc-levels.docx"
    convert_markdown_to_docx(fixtures_dir / "toc-levels.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    instr = _toc_field_paragraphs(root)[0].find(f".//{{{W_NS}}}instrText")
    assert 'TOC \\o "2-3"' in (instr.text or "")


def test_toc_with_sections(tmp_path: Path, fixtures_dir: Path):
    source = tmp_path / "toc-sections.md"
    source.write_text(
        "\n".join(
            [
                "<!-- toc -->",
                "",
                "# One",
                "",
                "<!-- section: landscape -->",
                "",
                "## Two",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "toc-sections.docx"
    convert_markdown_to_docx(source, output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    assert _toc_field_paragraphs(root)
    assert root.findall(f".//{{{W_NS}}}bookmarkStart")
