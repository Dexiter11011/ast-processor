"""Code block integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.code_block import CODE_BLOCK_STYLE
from md2docx.ooxml.style_ids import CODE_BLOCK, CODE_BLOCK_FONT
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_code_block(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "code-block.docx"
    convert_markdown_to_docx(fixtures_dir / "code-block.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        styles = etree.fromstring(zf.read("word/styles.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 1
    p = paragraphs[0]
    assert p.find(f".//{{{W_NS}}}pStyle").get(f"{{{W_NS}}}val") == CODE_BLOCK_STYLE
    run = p.find(f"{{{W_NS}}}r")
    assert run.find(f".//{{{W_NS}}}rFonts") is None
    texts = [t.text for t in run.findall(f"{{{W_NS}}}t")]
    assert texts == ["def hello():", "    return 'world'"]

    style = next(
        s for s in styles.findall(f"{{{W_NS}}}style") if s.get(f"{{{W_NS}}}styleId") == CODE_BLOCK
    )
    assert style is not None
    fonts = style.find(f".//{{{W_NS}}}rFonts")
    assert fonts.get(f"{{{W_NS}}}ascii") == CODE_BLOCK_FONT
