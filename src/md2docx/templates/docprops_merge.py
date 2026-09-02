"""Ensure docProps parts and root relationships exist in merged template packages."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.relationships import APP_PROPS_REL_TYPE, CORE_PROPS_REL_TYPE, PKG_NS
from md2docx.ooxml.xml_builder import ns_tag, serialize, sub_element

ROOT_RELS_PART = "_rels/.rels"

DOC_PROPS_TARGETS = (
    (CORE_PROPS_REL_TYPE, "docProps/core.xml"),
    (APP_PROPS_REL_TYPE, "docProps/app.xml"),
)


def _has_relationship(root: etree._Element, target: str) -> bool:
    for rel in root.findall(ns_tag(PKG_NS, "Relationship")):
        if rel.get("Target") == target:
            return True
    return False


def ensure_root_docprops_relationships(root_rels_xml: bytes) -> bytes:
    """Add docProps relationships to package root relationships when missing."""
    root = etree.fromstring(root_rels_xml)
    existing_ids = {
        rel.get("Id")
        for rel in root.findall(ns_tag(PKG_NS, "Relationship"))
        if rel.get("Id")
    }
    next_id = 1
    while f"rId{next_id}" in existing_ids:
        next_id += 1

    for rel_type, target in DOC_PROPS_TARGETS:
        if _has_relationship(root, target):
            continue
        rel_id = f"rId{next_id}"
        next_id += 1
        sub_element(
            root,
            "Relationship",
            attrs={"Id": rel_id, "Type": rel_type, "Target": target},
        )

    return serialize(root)


def ensure_docprops_package_parts(parts: dict[str, bytes]) -> None:
    """Ensure root relationships reference docProps when those parts are present."""
    if "docProps/core.xml" not in parts and "docProps/app.xml" not in parts:
        return
    if ROOT_RELS_PART in parts:
        parts[ROOT_RELS_PART] = ensure_root_docprops_relationships(parts[ROOT_RELS_PART])
