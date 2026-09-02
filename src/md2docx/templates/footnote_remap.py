"""Remap generated footnote IDs when merging into a template document."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, w_attr, w_tag


@dataclass
class FootnoteRemapMap:
    """Collected footnote ID remapping for generated content."""

    id_map: dict[str, str] = field(default_factory=dict)


def max_footnote_id(footnotes_xml: bytes) -> int:
    """Return the highest numeric footnote id in a footnotes part (excluding boilerplate)."""
    root = etree.fromstring(footnotes_xml)
    max_id = 0
    for node in root.iter(w_tag("footnote")):
        raw = node.get(w_attr("id"))
        if raw is None:
            continue
        try:
            value = int(raw)
        except ValueError:
            continue
        if value > 0 and value > max_id:
            max_id = value
    return max_id


def remap_footnote_ids(
    fragment: list[etree._Element],
    *,
    start_id: int,
) -> tuple[list[etree._Element], FootnoteRemapMap]:
    """Assign new footnote ids starting at *start_id* for generated content."""
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
        for node in clone.iter(w_tag("footnoteReference")):
            new_value = mapped(node.get(w_attr("id")))
            if new_value is not None:
                node.set(w_attr("id"), new_value)
        updated.append(clone)

    return updated, FootnoteRemapMap(id_map=id_map)


def remap_footnote_bodies(
    bodies: dict[int, list[etree._Element]],
    id_map: FootnoteRemapMap,
) -> dict[int, list[etree._Element]]:
    """Reorder footnote body paragraphs using remapped ids."""
    remapped: dict[int, list[etree._Element]] = {}
    for old_id, paragraphs in bodies.items():
        new_id = int(id_map.id_map.get(str(old_id), old_id))
        remapped[new_id] = [deepcopy(paragraph) for paragraph in paragraphs]
    return remapped


def merge_footnotes_xml(
    template_footnotes: bytes | None,
    generated_bodies: dict[int, list[etree._Element]],
) -> bytes:
    """Append generated footnote bodies to an existing or new footnotes part."""
    from md2docx.ooxml.footnote import build_footnotes_xml

    if template_footnotes is None:
        return build_footnotes_xml(generated_bodies)

    root = etree.fromstring(template_footnotes)
    for footnote_id in sorted(generated_bodies):
        footnote = etree.SubElement(root, w_tag("footnote"))
        footnote.set(w_attr("id"), str(footnote_id))
        for paragraph in generated_bodies[footnote_id]:
            footnote.append(deepcopy(paragraph))
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
