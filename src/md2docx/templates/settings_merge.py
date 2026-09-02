"""Ensure settings parts and relationships when dynamic fields are present."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.relationships import PKG_NS, SETTINGS_REL_TYPE
from md2docx.ooxml.settings import SETTINGS_PART, DocumentSettings, build_settings_xml, merge_update_fields_setting
from md2docx.ooxml.xml_builder import ns_tag, serialize, sub_element
from md2docx.templates.content_types_merge import merge_content_types
from md2docx.templates.package import CONTENT_TYPES_PART, DOCUMENT_RELS_PART


def _has_settings_relationship(document_rels_xml: bytes) -> bool:
    root = etree.fromstring(document_rels_xml)
    for rel in root.findall(ns_tag(PKG_NS, "Relationship")):
        if rel.get("Type") == SETTINGS_REL_TYPE:
            return True
    return False


def _add_settings_relationship(document_rels_xml: bytes) -> bytes:
    root = etree.fromstring(document_rels_xml)
    if _has_settings_relationship(document_rels_xml):
        return document_rels_xml
    existing_ids = {
        rel.get("Id")
        for rel in root.findall(ns_tag(PKG_NS, "Relationship"))
        if rel.get("Id")
    }
    next_id = 1
    while f"rId{next_id}" in existing_ids:
        next_id += 1
    sub_element(
        root,
        "Relationship",
        attrs={
            "Id": f"rId{next_id}",
            "Type": SETTINGS_REL_TYPE,
            "Target": "settings.xml",
        },
    )
    return serialize(root)


def ensure_settings_package_parts(parts: dict[str, bytes], *, update_fields_on_open: bool) -> None:
    """Add or update settings.xml and related package metadata."""
    if not update_fields_on_open:
        return

    if SETTINGS_PART in parts:
        parts[SETTINGS_PART] = merge_update_fields_setting(
            parts[SETTINGS_PART],
            update_fields_on_open=True,
        )
    else:
        parts[SETTINGS_PART] = build_settings_xml(
            DocumentSettings(update_fields_on_open=True)
        )

    if DOCUMENT_RELS_PART in parts:
        parts[DOCUMENT_RELS_PART] = _add_settings_relationship(parts[DOCUMENT_RELS_PART])

    if CONTENT_TYPES_PART in parts:
        parts[CONTENT_TYPES_PART] = merge_content_types(
            parts[CONTENT_TYPES_PART],
            media_extensions=set(),
            add_numbering=False,
            add_settings=True,
        )
