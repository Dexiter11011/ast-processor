"""Core properties OOXML tests."""

from datetime import datetime, timezone

from lxml import etree

from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.ooxml.core_props import build_core_props_xml

CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"


def test_build_core_props_xml():
    xml = build_core_props_xml(
        ResolvedDocumentMetadata(
            title="Sample Report",
            author="Jane Doe",
            subject="Metadata smoke test",
            keywords=("md2docx", "metadata", "docx"),
        ),
        now=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    root = etree.fromstring(xml)
    assert root.tag == f"{{{CP_NS}}}coreProperties"
    assert root.find(f"{{{DC_NS}}}title").text == "Sample Report"
    assert root.find(f"{{{DC_NS}}}creator").text == "Jane Doe"
    assert root.find(f"{{{DC_NS}}}subject").text == "Metadata smoke test"
    assert root.find(f"{{{CP_NS}}}keywords").text == "md2docx, metadata, docx"
    created = root.find("{http://purl.org/dc/terms/}created")
    assert created is not None
    assert created.text == "2026-01-01T12:00:00Z"


def test_build_core_props_xml_escapes_special_characters():
    xml = build_core_props_xml(
        ResolvedDocumentMetadata(
            title='Report & "Q1" <draft>',
            author="O'Brien & Co.",
            subject="A <subject> & more",
            keywords=("a&b", "c<d"),
        )
    )
    text = xml.decode("utf-8")
    assert "&amp;" in text
    assert "&lt;" in text
    assert "&gt;" in text
    assert 'Report & "Q1"' not in text

    root = etree.fromstring(xml)
    assert root.find(f"{{{DC_NS}}}title").text == 'Report & "Q1" <draft>'
    assert root.find(f"{{{DC_NS}}}creator").text == "O'Brien & Co."
    assert root.find(f"{{{DC_NS}}}subject").text == "A <subject> & more"
    assert root.find(f"{{{CP_NS}}}keywords").text == "a&b, c<d"
