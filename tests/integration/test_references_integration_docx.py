"""References integration fixture tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import R_NS, W_NS


def test_references_integration(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "references-integration.docx"
    convert_markdown_to_docx(fixtures_dir / "references-integration.md", output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        rels = zf.read("word/_rels/document.xml.rels").decode()
        styles = zf.read("word/styles.xml").decode()

    assert "TOC1" in styles
    toc_instr = root.find(f".//{{{W_NS}}}instrText")
    assert toc_instr is not None
    assert "TOC" in (toc_instr.text or "")

    bookmarks = root.findall(f".//{{{W_NS}}}bookmarkStart")
    assert len(bookmarks) >= 4

    internal = [h for h in root.findall(f".//{{{W_NS}}}hyperlink") if h.get(f"{{{W_NS}}}anchor")]
    external = [h for h in root.findall(f".//{{{W_NS}}}hyperlink") if h.get(f"{{{R_NS}}}id")]
    assert internal
    assert external
    assert internal[0].get(f"{{{W_NS}}}anchor") == "architecture"
    assert 'Target="https://example.com"' in rels
