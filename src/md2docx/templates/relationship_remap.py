"""Remap generated relationship IDs when merging into a template package."""

from __future__ import annotations

import re
from copy import deepcopy

from lxml import etree

from md2docx.ooxml.relationships import (
    FOOTER_REL_TYPE,
    FOOTNOTES_REL_TYPE,
    HEADER_REL_TYPE,
    HYPERLINK_REL_TYPE,
    IMAGE_REL_TYPE,
    NUMBERING_REL_TYPE,
    STYLES_REL_TYPE,
    Relationship,
)
from md2docx.ooxml.xml_builder import PKG_NS, R_NS, ns_tag, serialize, w_tag

R_ID_ATTR = f"{{{R_NS}}}id"
R_EMBED_ATTR = f"{{{R_NS}}}embed"
_REL_ID_RE = re.compile(r"^rId(\d+)$")


def _max_rel_number(rel_ids: set[str]) -> int:
    max_id = 0
    for rel_id in rel_ids:
        match = _REL_ID_RE.match(rel_id)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return max_id


def _parse_document_rels(rels_xml: bytes) -> etree._Element:
    return etree.fromstring(rels_xml)


def _existing_relationships(root: etree._Element) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for rel in root.findall(ns_tag(PKG_NS, "Relationship")):
        rel_id = rel.get("Id") or ""
        rel_type = rel.get("Type") or ""
        target = rel.get("Target") or ""
        rows.append((rel_id, rel_type, target))
    return rows


def rewrite_relationship_ids(
    fragment: list[etree._Element],
    rel_id_map: dict[str, str],
) -> list[etree._Element]:
    if not rel_id_map:
        return fragment
    updated: list[etree._Element] = []
    for element in fragment:
        clone = deepcopy(element)
        for node in clone.iter():
            for attr in (R_ID_ATTR, R_EMBED_ATTR):
                current = node.get(attr)
                if current in rel_id_map:
                    node.set(attr, rel_id_map[current])
        updated.append(clone)
    return updated


def merge_document_relationships(
    template_rels_xml: bytes,
    generated_relationships: list[Relationship],
    *,
    media_target_map: dict[str, str],
    add_numbering_relationship: bool,
) -> tuple[bytes, dict[str, str]]:
    """Append generated relationships to template document.xml.rels with new rIds."""
    root = _parse_document_rels(template_rels_xml)
    existing = _existing_relationships(root)
    existing_ids = {rel_id for rel_id, _, _ in existing}
    rel_type_to_id = {rel_type: rel_id for rel_id, rel_type, _ in existing}
    next_id = _max_rel_number(existing_ids) + 1
    rel_id_map: dict[str, str] = {}

    for rel in generated_relationships:
        if rel.rel_type == STYLES_REL_TYPE:
            template_styles_id = rel_type_to_id.get(STYLES_REL_TYPE, rel.rel_id)
            rel_id_map[rel.rel_id] = template_styles_id
            continue
        if rel.rel_type == NUMBERING_REL_TYPE:
            if add_numbering_relationship:
                target = rel.target
                new_rel_id = f"rId{next_id}"
                next_id += 1
                rel_id_map[rel.rel_id] = new_rel_id
                etree.SubElement(
                    root,
                    ns_tag(PKG_NS, "Relationship"),
                    {"Id": new_rel_id, "Type": rel.rel_type, "Target": target},
                )
            else:
                template_numbering_id = rel_type_to_id.get(NUMBERING_REL_TYPE, rel.rel_id)
                rel_id_map[rel.rel_id] = template_numbering_id
            continue
        if rel.rel_type == FOOTNOTES_REL_TYPE:
            template_footnotes_id = rel_type_to_id.get(FOOTNOTES_REL_TYPE)
            if template_footnotes_id is None:
                new_rel_id = f"rId{next_id}"
                next_id += 1
                rel_id_map[rel.rel_id] = new_rel_id
                etree.SubElement(
                    root,
                    ns_tag(PKG_NS, "Relationship"),
                    {
                        "Id": new_rel_id,
                        "Type": rel.rel_type,
                        "Target": rel.target,
                    },
                )
            else:
                rel_id_map[rel.rel_id] = template_footnotes_id
            continue
        if rel.rel_type in (HEADER_REL_TYPE, FOOTER_REL_TYPE):
            rel_id_map[rel.rel_id] = rel.rel_id
            continue

        target = media_target_map.get(rel.target, rel.target)
        new_rel_id = f"rId{next_id}"
        next_id += 1
        rel_id_map[rel.rel_id] = new_rel_id

        attrs = {"Id": new_rel_id, "Type": rel.rel_type, "Target": target}
        if rel.target_mode:
            attrs["TargetMode"] = rel.target_mode
        etree.SubElement(root, ns_tag(PKG_NS, "Relationship"), attrs)

    return serialize(root), rel_id_map


def resolve_media_collisions(
    template_parts: dict[str, bytes],
    generated_media: dict[str, bytes],
) -> tuple[dict[str, bytes], dict[str, str]]:
    """Rename generated media parts that collide with template media paths."""
    merged: dict[str, bytes] = {}
    target_map: dict[str, str] = {}
    used_names = set(template_parts)

    for part_path, data in generated_media.items():
        if part_path not in used_names:
            merged[part_path] = data
            used_names.add(part_path)
            continue

        suffix = part_path.removeprefix("word/")
        old_target = suffix if suffix.startswith("media/") else f"media/{suffix.split('/')[-1]}"
        stem_path = part_path.rsplit(".", 1)
        if len(stem_path) == 2:
            stem, ext = stem_path[0], stem_path[1]
        else:
            stem, ext = part_path, "bin"
        counter = 1
        while True:
            candidate = f"{stem}-gen{counter}.{ext}"
            if candidate not in used_names:
                merged[candidate] = data
                used_names.add(candidate)
                new_suffix = candidate.removeprefix("word/")
                new_target = (
                    new_suffix if new_suffix.startswith("media/") else f"media/{new_suffix.split('/')[-1]}"
                )
                target_map[old_target] = new_target
                break
            counter += 1

    return merged, target_map
