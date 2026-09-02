"""Unit tests for DOCX package validator."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md2docx.ooxml.content_types import build_content_types_xml
from md2docx.ooxml.relationships import RelationshipManager
from md2docx.ooxml.styles import build_minimal_styles_xml
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_attr, w_tag
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import DocxPackage, validate_docx, validate_docx_bytes
from md2docx.validation.package_validator import DocxValidator


def _minimal_docx_parts(*, include_numbering: bool = False) -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    paragraph = etree.SubElement(body, w_tag("p"))
    run = etree.SubElement(paragraph, w_tag("r"))
    text = etree.SubElement(run, w_tag("t"))
    text.text = "Hello"
    sect_pr = etree.SubElement(body, w_tag("sectPr"))
    pg_sz = etree.SubElement(sect_pr, w_tag("pgSz"))
    pg_sz.set(w_tag("w"), "11906")
    pg_sz.set(w_tag("h"), "16838")
    doc_root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    doc_root.append(body)
    parts = {
        "[Content_Types].xml": build_content_types_xml(has_numbering=include_numbering),
        "_rels/.rels": rels.build_root_rels_xml(),
        "word/document.xml": serialize(doc_root),
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    return parts


def _write_docx(parts: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(parts):
            zf.writestr(name, parts[name])
    return buf.getvalue()


def test_minimal_generated_docx_is_valid():
    report = validate_docx_bytes(_write_docx(_minimal_docx_parts()))
    assert report.ok, report.format_messages()


def test_detects_malformed_xml():
    parts = _minimal_docx_parts()
    parts["word/document.xml"] = b"<w:document><unclosed>"
    report = DocxValidator(DocxPackage.from_bytes(_write_docx(parts))).validate()
    assert not report.ok
    assert any(issue.category == "xml" for issue in report.issues)


def test_detects_dangling_relationship_reference():
    parts = _minimal_docx_parts()
    doc = etree.fromstring(parts["word/document.xml"])
    p = doc.find(f".//{{{W_NS}}}p")
    hyperlink = etree.SubElement(
        p,
        w_tag("hyperlink"),
        nsmap={"w": W_NS, "r": R_NS},
    )
    hyperlink.set(f"{{{R_NS}}}id", "rId999")
    parts["word/document.xml"] = serialize(doc)
    report = DocxValidator(DocxPackage.from_bytes(_write_docx(parts))).validate()
    assert not report.ok
    assert any(issue.category == "references" for issue in report.issues)


def test_detects_unknown_num_id(fixtures_dir: Path, tmp_path: Path):
    convert_markdown_to_docx(fixtures_dir / "ordered-list.md", tmp_path / "list.docx")
    package = DocxPackage.from_path(tmp_path / "list.docx")
    doc = etree.fromstring(package.parts["word/document.xml"])
    num_id = doc.find(f".//{{{W_NS}}}numId")
    num_id.set(w_attr("val"), "99999")
    package.parts["word/document.xml"] = serialize(doc)
    report = DocxValidator(package).validate()
    assert not report.ok
    assert any(issue.category == "numbering" for issue in report.issues)


def test_unicode_fixture_validates(fixtures_dir: Path, tmp_path: Path):
    convert_markdown_to_docx(fixtures_dir / "escaping-edge-cases.md", tmp_path / "unicode.docx")
    report = validate_docx(tmp_path / "unicode.docx")
    assert report.ok, report.format_messages()
