"""XML escaping integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import HYPERLINK_REL_TYPE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _all_texts(root: etree._Element) -> list[str]:
    return [t.text for t in root.findall(f".//{{{W_NS}}}t") if t.text is not None]


def test_pipeline_xml_escaping(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "xml-escaping.docx"
    convert_markdown_to_docx(fixtures_dir / "xml-escaping.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        doc_bytes = zf.read("word/document.xml")
        rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        root = etree.fromstring(doc_bytes)

    assert b"&amp;" in doc_bytes or b"&lt;" in doc_bytes
    texts = _all_texts(root)
    joined = "".join(texts)
    assert 'A & B <tag> "quote" \'apos\'' in joined
    assert "bold & <x>" in joined
    assert "italic & <y>" in joined
    assert "code & <>" in joined
    assert "link" in joined
    assert "x < y && z" in joined
    assert "quote & <z>" in joined
    assert "item & <w>" in joined

    assert 'Target="https://example.com?q=a&amp;b=1"' in rels_xml
    assert HYPERLINK_REL_TYPE in rels_xml
