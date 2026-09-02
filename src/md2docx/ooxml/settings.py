"""word/settings.xml builder."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, serialize, w_attr, w_tag

SETTINGS_PART = "word/settings.xml"
SETTINGS_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"
)


@dataclass
class DocumentSettings:
    """Document-level Word settings."""

    update_fields_on_open: bool = False


def build_settings_xml(settings: DocumentSettings) -> bytes:
    root = etree.Element(w_tag("settings"), nsmap={"w": W_NS})
    if settings.update_fields_on_open:
        update_fields = etree.SubElement(root, w_tag("updateFields"))
        update_fields.set(w_attr("val"), "true")
    return serialize(root)


def merge_update_fields_setting(settings_xml: bytes, *, update_fields_on_open: bool) -> bytes:
    """Ensure updateFields is present in an existing settings part."""
    root = etree.fromstring(settings_xml)
    existing = root.find(w_tag("updateFields"))
    if update_fields_on_open:
        if existing is None:
            existing = etree.SubElement(root, w_tag("updateFields"))
        existing.set(w_attr("val"), "true")
    elif existing is not None:
        root.remove(existing)
    return serialize(root)
