"""Merge template and theme styles.xml content."""

from __future__ import annotations

from copy import deepcopy

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, w_attr, w_tag


def merge_template_and_theme_styles(template_styles: bytes, theme_styles: bytes) -> bytes:
    """Use template styles as base and override/add styles from the active theme."""
    template_root = etree.fromstring(template_styles)
    theme_root = etree.fromstring(theme_styles)

    existing = {
        style.get(w_attr("styleId")): style
        for style in template_root.findall(w_tag("style"))
        if style.get(w_attr("styleId"))
    }

    for style in theme_root.findall(w_tag("style")):
        style_id = style.get(w_attr("styleId"))
        if not style_id:
            continue
        current = existing.get(style_id)
        if current is not None:
            parent = current.getparent()
            if parent is not None:
                index = parent.index(current)
                parent.remove(current)
                parent.insert(index, deepcopy(style))
        else:
            template_root.append(deepcopy(style))
        existing[style_id] = style

    doc_defaults = theme_root.find(w_tag("docDefaults"))
    if doc_defaults is not None:
        current_defaults = template_root.find(w_tag("docDefaults"))
        if current_defaults is not None:
            parent = current_defaults.getparent()
            if parent is not None:
                index = parent.index(current_defaults)
                parent.remove(current_defaults)
                parent.insert(index, deepcopy(doc_defaults))
        else:
            template_root.insert(0, deepcopy(doc_defaults))

    return etree.tostring(template_root, xml_declaration=True, encoding="UTF-8", standalone=True)


def template_style_ids(styles_xml: bytes) -> set[str]:
    root = etree.fromstring(styles_xml)
    return {
        style.get(w_attr("styleId"))
        for style in root.findall(w_tag("style"))
        if style.get(w_attr("styleId"))
    }
