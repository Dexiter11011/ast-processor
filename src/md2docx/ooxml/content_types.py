"""[Content_Types].xml generator."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import CT_NS, ns_tag, serialize, sub_element

_EXT_TO_CT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
}


def build_content_types_xml(
    *,
    has_numbering: bool = False,
    has_footnotes: bool = False,
    has_doc_props: bool = False,
    has_settings: bool = False,
    media_extensions: set[str] | None = None,
    header_parts: list[str] | None = None,
    footer_parts: list[str] | None = None,
) -> bytes:
    root = etree.Element(ns_tag(CT_NS, "Types"), nsmap={None: CT_NS})
    sub_element(root, "Default", attrs={"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    sub_element(root, "Default", attrs={"Extension": "xml", "ContentType": "application/xml"})
    for ext in sorted(media_extensions or ()):
        content_type = _EXT_TO_CT.get(ext, "application/octet-stream")
        sub_element(root, "Default", attrs={"Extension": ext, "ContentType": content_type})
    sub_element(
        root,
        "Override",
        attrs={
            "PartName": "/word/document.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
        },
    )
    sub_element(
        root,
        "Override",
        attrs={
            "PartName": "/word/styles.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
        },
    )
    if has_numbering:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": "/word/numbering.xml",
                "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
            },
        )
    if has_footnotes:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": "/word/footnotes.xml",
                "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
            },
        )
    if has_settings:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": "/word/settings.xml",
                "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
            },
        )
    for part_path in header_parts or []:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": f"/{part_path}",
                "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml",
            },
        )
    for part_path in footer_parts or []:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": f"/{part_path}",
                "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml",
            },
        )
    if has_doc_props:
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": "/docProps/core.xml",
                "ContentType": "application/vnd.openxmlformats-package.core-properties+xml",
            },
        )
        sub_element(
            root,
            "Override",
            attrs={
                "PartName": "/docProps/app.xml",
                "ContentType": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
            },
        )
    return serialize(root)
