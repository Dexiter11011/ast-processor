"""Remap generated bookmark IDs and names when merging into a template document."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, w_attr, w_tag

_REF_INSTR_RE = re.compile(
    r"(\s*REF\s+)([A-Za-z][A-Za-z0-9_\-]{0,39})(\s+\\.+|\s*$)",
    re.IGNORECASE,
)


@dataclass
class BookmarkRemapMap:
    """Collected bookmark remapping for generated content."""

    id_map: dict[str, str] = field(default_factory=dict)
    name_map: dict[str, str] = field(default_factory=dict)


def collect_bookmark_names(document_xml: bytes) -> set[str]:
    """Return all bookmark names present in a document part."""
    root = etree.fromstring(document_xml)
    names: set[str] = set()
    for node in root.iter(w_tag("bookmarkStart")):
        name = node.get(w_attr("name"))
        if name:
            names.add(name)
    return names


def collect_fragment_bookmark_names(fragment: list[etree._Element]) -> set[str]:
    names: set[str] = set()
    for element in fragment:
        for node in element.iter(w_tag("bookmarkStart")):
            name = node.get(w_attr("name"))
            if name:
                names.add(name)
    return names


def build_name_collision_remap(
    generated_names: set[str],
    reserved_names: set[str],
) -> dict[str, str]:
    """Build old_name -> new_name map for generated bookmarks colliding with template."""
    name_map: dict[str, str] = {}
    occupied = set(reserved_names)
    for name in sorted(generated_names):
        if name not in occupied:
            occupied.add(name)
            continue
        counter = 1
        while True:
            candidate = f"{name}-{counter}"
            if candidate not in occupied:
                name_map[name] = candidate
                occupied.add(candidate)
                break
            counter += 1
    return name_map


def _rewrite_ref_instruction(instruction: str, name_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group(2)
        new_target = name_map.get(target, target)
        return f"{match.group(1)}{new_target}{match.group(3)}"

    return _REF_INSTR_RE.sub(repl, instruction)


def _apply_name_remap(clone: etree._Element, name_map: dict[str, str]) -> None:
    if not name_map:
        return
    for node in clone.iter(w_tag("bookmarkStart")):
        name = node.get(w_attr("name"))
        if name and name in name_map:
            node.set(w_attr("name"), name_map[name])
    for node in clone.iter(w_tag("hyperlink")):
        anchor = node.get(w_attr("anchor"))
        if anchor and anchor in name_map:
            node.set(w_attr("anchor"), name_map[anchor])
    for node in clone.iter(w_tag("instrText")):
        text = node.text or ""
        if "REF" in text.upper():
            node.text = _rewrite_ref_instruction(text, name_map)
    for node in clone.iter(w_tag("fldSimple")):
        instruction = node.get(w_attr("instr")) or ""
        if "REF" in instruction.upper():
            node.set(w_attr("instr"), _rewrite_ref_instruction(instruction, name_map))


def remap_bookmark_ids(fragment: list[etree._Element], start_id: int) -> list[etree._Element]:
    """Assign new bookmark ids starting at *start_id* for generated content."""
    updated, _ = remap_bookmarks(fragment, start_id=start_id, reserved_names=set())
    return updated


def remap_bookmarks(
    fragment: list[etree._Element],
    *,
    start_id: int,
    reserved_names: set[str],
) -> tuple[list[etree._Element], BookmarkRemapMap]:
    """Remap bookmark IDs and resolve name collisions against template bookmarks."""
    generated_names = collect_fragment_bookmark_names(fragment)
    name_map = build_name_collision_remap(generated_names, reserved_names)
    id_map: dict[str, str] = {}
    next_id = start_id

    def mapped(raw: str | None) -> str | None:
        nonlocal next_id
        if raw is None:
            return None
        if raw not in id_map:
            id_map[raw] = str(next_id)
            next_id += 1
        return id_map[raw]

    updated: list[etree._Element] = []
    for element in fragment:
        clone = deepcopy(element)
        for tag in (w_tag("bookmarkStart"), w_tag("bookmarkEnd")):
            for node in clone.iter(tag):
                new_value = mapped(node.get(w_attr("id")))
                if new_value is not None:
                    node.set(w_attr("id"), new_value)
        _apply_name_remap(clone, name_map)
        updated.append(clone)

    return updated, BookmarkRemapMap(id_map=id_map, name_map=name_map)
