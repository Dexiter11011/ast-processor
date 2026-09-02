"""Document metadata integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import APP_PROPS_REL_TYPE, CORE_PROPS_REL_TYPE
from md2docx.pipeline import convert_markdown_to_docx

CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def test_pipeline_document_metadata(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "document-metadata.docx"
    convert_markdown_to_docx(fixtures_dir / "document-metadata.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        names = set(zf.namelist())
        core = etree.fromstring(zf.read("docProps/core.xml"))
        app = etree.fromstring(zf.read("docProps/app.xml"))
        root_rels = etree.fromstring(zf.read("_rels/.rels"))
        doc_root = etree.fromstring(zf.read("word/document.xml"))

    assert "docProps/core.xml" in names
    assert "docProps/app.xml" in names
    assert core.find(f"{{{DC_NS}}}title").text == "Sample Report"
    assert core.find(f"{{{DC_NS}}}creator").text == "Jane Doe"
    assert core.find(f"{{{DC_NS}}}subject").text == "Metadata smoke test"
    assert core.find(f"{{{CP_NS}}}keywords").text == "md2docx, metadata, docx"
    assert app.find("{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Application").text == "md2docx"

    rel_types = {rel.get("Type") for rel in root_rels.findall(f"{{{PKG_REL_NS}}}Relationship")}
    assert CORE_PROPS_REL_TYPE in rel_types
    assert APP_PROPS_REL_TYPE in rel_types

    assert doc_root.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t").text == "Report"
