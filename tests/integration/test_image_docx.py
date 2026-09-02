"""Image integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import IMAGE_REL_TYPE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def test_pipeline_image(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "image.docx"
    convert_markdown_to_docx(fixtures_dir / "image.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        names = zf.namelist()
        doc_xml = zf.read("word/document.xml")
        rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        root = etree.fromstring(doc_xml)

    assert any(name.startswith("word/media/image1.") for name in names)
    drawing = root.find(f".//{{{W_NS}}}drawing")
    assert drawing is not None
    blip = drawing.find(f".//{{{A_NS}}}blip")
    assert blip is not None
    rel_id = blip.get(f"{{{R_NS}}}embed")
    assert rel_id == "rId2"
    assert f'Id="{rel_id}"' in rels_xml
    assert 'Target="media/image1.png"' in rels_xml
    assert IMAGE_REL_TYPE in rels_xml
    assert root.find(f".//{{{W_NS}}}t").text == "Logo"
