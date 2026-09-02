"""Merge [Content_Types].xml when adding generated package parts."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.content_types import _EXT_TO_CT
from md2docx.ooxml.xml_builder import CT_NS, ns_tag, serialize

NUMBERING_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"
)
CORE_PROPS_CONTENT_TYPE = (
    "application/vnd.openxmlformats-package.core-properties+xml"
)
APP_PROPS_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.extended-properties+xml"
)
SETTINGS_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"
)
FOOTNOTES_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"
)
SETTINGS_PART = "/word/settings.xml"
FOOTNOTES_PART = "/word/footnotes.xml"


def _has_override(root: etree._Element, part_name: str) -> bool:
    for override in root.findall(ns_tag(CT_NS, "Override")):
        if override.get("PartName") == part_name:
            return True
    return False


def _has_default_ext(root: etree._Element, ext: str) -> bool:
    for default in root.findall(ns_tag(CT_NS, "Default")):
        if default.get("Extension") == ext:
            return True
    return False


def merge_content_types(
    template_content_types: bytes,
    *,
    media_extensions: set[str],
    add_numbering: bool,
    add_doc_props: bool = False,
    add_settings: bool = False,
    add_footnotes: bool = False,
) -> bytes:
    root = etree.fromstring(template_content_types)

    for ext in sorted(media_extensions):
        if _has_default_ext(root, ext):
            continue
        content_type = _EXT_TO_CT.get(ext, "application/octet-stream")
        etree.SubElement(
            root,
            ns_tag(CT_NS, "Default"),
            {"Extension": ext, "ContentType": content_type},
        )

    if add_numbering and not _has_override(root, "/word/numbering.xml"):
        etree.SubElement(
            root,
            ns_tag(CT_NS, "Override"),
            {"PartName": "/word/numbering.xml", "ContentType": NUMBERING_CONTENT_TYPE},
        )

    if add_doc_props:
        for part_name, content_type in (
            ("/docProps/core.xml", CORE_PROPS_CONTENT_TYPE),
            ("/docProps/app.xml", APP_PROPS_CONTENT_TYPE),
        ):
            if not _has_override(root, part_name):
                etree.SubElement(
                    root,
                    ns_tag(CT_NS, "Override"),
                    {"PartName": part_name, "ContentType": content_type},
                )

    if add_settings and not _has_override(root, SETTINGS_PART):
        etree.SubElement(
            root,
            ns_tag(CT_NS, "Override"),
            {"PartName": SETTINGS_PART, "ContentType": SETTINGS_CONTENT_TYPE},
        )

    if add_footnotes and not _has_override(root, FOOTNOTES_PART):
        etree.SubElement(
            root,
            ns_tag(CT_NS, "Override"),
            {"PartName": FOOTNOTES_PART, "ContentType": FOOTNOTES_CONTENT_TYPE},
        )

    return serialize(root)
