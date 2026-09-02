"""Remap generated numbering definitions when merging into a template package."""

from __future__ import annotations

from copy import deepcopy

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, serialize, w_attr, w_tag


def _max_numeric_attr(root: etree._Element, tag: str, attr: str) -> int:
    maximum = -1
    for node in root.findall(tag):
        raw = node.get(w_attr(attr))
        if raw is not None and raw.isdigit():
            maximum = max(maximum, int(raw))
    return maximum


def _remap_num_ids(fragment: list[etree._Element], num_id_map: dict[str, str]) -> list[etree._Element]:
    if not num_id_map:
        return fragment
    updated: list[etree._Element] = []
    for element in fragment:
        clone = deepcopy(element)
        for num_id_el in clone.iter(w_tag("numId")):
            current = num_id_el.get(w_attr("val"))
            if current in num_id_map:
                num_id_el.set(w_attr("val"), num_id_map[current])
        updated.append(clone)
    return updated


def merge_numbering(
    template_numbering: bytes | None,
    generated_numbering: bytes | None,
    fragment: list[etree._Element],
) -> tuple[list[etree._Element], bytes | None, bool]:
    """Merge generated numbering into template numbering and remap fragment numIds.

    Returns updated fragment, merged numbering bytes, and whether a new numbering
    relationship must be added to document.xml.rels.
    """
    if generated_numbering is None:
        return fragment, template_numbering, False

    generated_root = etree.fromstring(generated_numbering)
    if template_numbering is None:
        num_id_map = {
            node.get(w_attr("numId")): node.get(w_attr("numId"))
            for node in generated_root.findall(w_tag("num"))
            if node.get(w_attr("numId"))
        }
        return fragment, generated_numbering, True

    template_root = etree.fromstring(template_numbering)
    next_abstract = _max_numeric_attr(template_root, w_tag("abstractNum"), "abstractNumId") + 1
    next_num = _max_numeric_attr(template_root, w_tag("num"), "numId") + 1

    abstract_map: dict[str, str] = {}
    for abstract in generated_root.findall(w_tag("abstractNum")):
        old = abstract.get(w_attr("abstractNumId"))
        if old is None:
            continue
        new = str(next_abstract)
        next_abstract += 1
        abstract.set(w_attr("abstractNumId"), new)
        abstract_map[old] = new
        template_root.append(deepcopy(abstract))

    num_id_map: dict[str, str] = {}
    for num in generated_root.findall(w_tag("num")):
        old = num.get(w_attr("numId"))
        if old is None:
            continue
        new = str(next_num)
        next_num += 1
        num.set(w_attr("numId"), new)
        abstract_ref = num.find(w_tag("abstractNumId"))
        if abstract_ref is not None:
            ref_val = abstract_ref.get(w_attr("val"))
            if ref_val in abstract_map:
                abstract_ref.set(w_attr("val"), abstract_map[ref_val])
        num_id_map[old] = new
        template_root.append(deepcopy(num))

    updated_fragment = _remap_num_ids(fragment, num_id_map)
    return updated_fragment, serialize(template_root), False
