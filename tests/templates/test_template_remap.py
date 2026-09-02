"""Unit tests for template remapping helpers."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.numbering import NumberingManager
from md2docx.ooxml.relationships import (
    HYPERLINK_REL_TYPE,
    IMAGE_REL_TYPE,
    STYLES_REL_TYPE,
    Relationship,
)
from md2docx.ooxml.xml_builder import PKG_NS, R_NS, W_NS, ns_tag, serialize, w_attr, w_tag
from md2docx.templates.bookmark_remap import remap_bookmark_ids
from md2docx.templates.numbering_remap import merge_numbering
from md2docx.templates.relationship_remap import merge_document_relationships, rewrite_relationship_ids


def _sample_document_rels() -> bytes:
    root = etree.Element(ns_tag(PKG_NS, "Relationships"), nsmap={None: PKG_NS})
    etree.SubElement(
        root,
        ns_tag(PKG_NS, "Relationship"),
        {
            "Id": "rId1",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles",
            "Target": "styles.xml",
        },
    )
    etree.SubElement(
        root,
        ns_tag(PKG_NS, "Relationship"),
        {
            "Id": "rId2",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header",
            "Target": "header1.xml",
        },
    )
    return serialize(root)


def test_merge_document_relationships_allocates_new_ids():
    generated = [
        Relationship("rId1", STYLES_REL_TYPE, "styles.xml"),
        Relationship("rId2", IMAGE_REL_TYPE, "media/image1.png"),
        Relationship("rId3", HYPERLINK_REL_TYPE, "https://example.com", "External"),
    ]
    rels, mapping = merge_document_relationships(
        _sample_document_rels(),
        generated,
        media_target_map={},
        add_numbering_relationship=False,
    )
    assert mapping["rId1"] == "rId1"
    assert mapping["rId2"] == "rId3"
    assert mapping["rId3"] == "rId4"
    assert b"rId4" in rels


def test_rewrite_relationship_ids_updates_embed_attributes():
    fragment = [
        api.image_paragraph(rel_id="rId2", width_emu=1000, height_emu=1000, doc_pr_id=1, name="x")
    ]
    updated = rewrite_relationship_ids(fragment, {"rId2": "rId9"})
    embed_attr = f"{{{R_NS}}}embed"
    values = [
        node.get(embed_attr)
        for node in updated[0].iter()
        if node.get(embed_attr) is not None
    ]
    assert values == ["rId9"]


def test_merge_numbering_remaps_generated_num_ids():
    numbering = NumberingManager()
    num_id = numbering.allocate_num_id(ordered=False)
    generated_xml = numbering.to_bytes()
    paragraph = api.paragraph([], style_id="ListParagraph", num_id=num_id, num_level=0)
    template_numbering = serialize(
        etree.Element(w_tag("numbering"), nsmap={"w": W_NS})
    )
    fragment, merged, _add_rel = merge_numbering(template_numbering, generated_xml, [paragraph])
    num_el = fragment[0].find(f".//{w_tag('numId')}")
    assert num_el is not None
    assert num_el.get(w_attr("val")) == str(num_id - 1)
    assert merged is not None
    assert b"abstractNum" in merged


def test_remap_bookmark_ids_offsets_generated_bookmarks():
    start = etree.Element(w_tag("bookmarkStart"))
    start.set(w_attr("id"), "0")
    end = etree.Element(w_tag("bookmarkEnd"))
    end.set(w_attr("id"), "0")
    paragraph = api.paragraph([], style_id="Heading1")
    paragraph.insert(0, start)
    paragraph.append(end)
    updated = remap_bookmark_ids([paragraph], start_id=5)
    new_start = updated[0].find(w_tag("bookmarkStart"))
    assert new_start is not None
    assert new_start.get(w_attr("id")) == "5"
