"""Hyperlink integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def test_external_links_deduplicate_relationships(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "external-links.docx"
    convert_markdown_to_docx(fixtures_dir / "external-links.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        rels = zf.read("word/_rels/document.xml.rels").decode()
        root = etree.fromstring(zf.read("word/document.xml"))
    assert rels.count('Target="https://example.com"') == 1
    assert 'Target="https://other.example"' in rels
    hyperlinks = root.findall(f".//{{{W_NS}}}hyperlink")
    assert len(hyperlinks) == 3
    for hyper in hyperlinks:
        assert hyper.get(f"{{{R_NS}}}id") is not None
        assert hyper.get(f"{{{W_NS}}}anchor") is None


def test_internal_link_uses_anchor_not_relationship(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "internal-links.docx"
    convert_markdown_to_docx(fixtures_dir / "internal-links.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        rels = zf.read("word/_rels/document.xml.rels").decode()
        root = etree.fromstring(zf.read("word/document.xml"))
    assert 'Target="#' not in rels
    internal = [h for h in root.findall(f".//{{{W_NS}}}hyperlink") if h.get(f"{{{W_NS}}}anchor")]
    assert len(internal) == 1
    assert internal[0].get(f"{{{W_NS}}}anchor") == "introduction"
    assert internal[0].get(f"{{{R_NS}}}id") is None
    starts = root.findall(f".//{{{W_NS}}}bookmarkStart")
    assert len(starts) >= 2


def test_broken_internal_link_renders_plain_text(tmp_path: Path):
    source = tmp_path / "broken.md"
    source.write_text("[Missing](#does-not-exist)\n", encoding="utf-8")
    output = tmp_path / "broken.docx"
    convert_markdown_to_docx(source, output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    assert root.findall(f".//{{{W_NS}}}hyperlink") == []
    texts = "".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "Missing" in texts
