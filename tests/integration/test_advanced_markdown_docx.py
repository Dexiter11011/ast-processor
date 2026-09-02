"""Integration tests for footnotes, definition lists, and safe HTML."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_footnotes_package_parts(tmp_path: Path):
    source = tmp_path / "doc.md"
    source.write_text(
        "Reference[^1].\n\n[^1]: Footnote body.\n",
        encoding="utf-8",
    )
    output = tmp_path / "doc.docx"
    convert_markdown_to_docx(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
        assert "word/footnotes.xml" in names
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        assert "footnotes.xml" in rels
        doc = etree.fromstring(zf.read("word/document.xml"))
        footnote_refs = doc.findall(f".//{{{W_NS}}}footnoteReference")
        assert len(footnote_refs) == 1
        footnotes = etree.fromstring(zf.read("word/footnotes.xml"))
        user_notes = [
            node
            for node in footnotes.findall(f".//{{{W_NS}}}footnote")
            if node.get(f"{{{W_NS}}}id") not in ("-1", "0")
        ]
        assert len(user_notes) == 1


def test_definition_list_renders(tmp_path: Path):
    source = tmp_path / "doc.md"
    source.write_text("Term\n: Description paragraph.\n", encoding="utf-8")
    output = tmp_path / "doc.docx"
    convert_markdown_to_docx(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        doc = etree.fromstring(zf.read("word/document.xml"))
        texts = [t.text for t in doc.findall(f".//{{{W_NS}}}t") if t.text]
        joined = "".join(texts)
        assert "Term" in joined
        assert "Description paragraph." in joined
