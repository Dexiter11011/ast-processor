"""docProps/core.xml builder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Union

from lxml import etree

from md2docx.ast.metadata import DocumentMetadata
from md2docx.ooxml.xml_builder import ns_tag, serialize, sub_element

if TYPE_CHECKING:
    from md2docx.metadata.resolved import ResolvedDocumentMetadata

_CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_DCTERMS_NS = "http://purl.org/dc/terms/"
_XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

MetadataInput = Union["DocumentMetadata", "ResolvedDocumentMetadata"]


def _coerce_metadata(metadata: MetadataInput) -> "ResolvedDocumentMetadata":
    from md2docx.metadata.resolved import ResolvedDocumentMetadata

    if isinstance(metadata, ResolvedDocumentMetadata):
        return metadata
    keywords = tuple(
        part.strip()
        for part in (metadata.keywords or "").split(",")
        if part.strip()
    )
    return ResolvedDocumentMetadata(
        title=metadata.title or None,
        author=metadata.author or None,
        subject=metadata.subject or None,
        keywords=keywords,
    )


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_core_props_xml(
    metadata: MetadataInput,
    *,
    now: datetime | None = None,
) -> bytes:
    resolved = _coerce_metadata(metadata)
    timestamp = now or datetime.now(timezone.utc)
    created = resolved.created or timestamp
    modified = resolved.modified or timestamp

    root = etree.Element(
        ns_tag(_CP_NS, "coreProperties"),
        nsmap={
            "cp": _CP_NS,
            "dc": _DC_NS,
            "dcterms": _DCTERMS_NS,
            "xsi": _XSI_NS,
        },
    )
    if resolved.title:
        sub_element(root, "title", ns=_DC_NS, text=resolved.title)
    if resolved.subject:
        sub_element(root, "subject", ns=_DC_NS, text=resolved.subject)
    if resolved.author:
        sub_element(root, "creator", ns=_DC_NS, text=resolved.author)
        sub_element(root, "lastModifiedBy", ns=_CP_NS, text=resolved.author)
    if resolved.keywords:
        sub_element(root, "keywords", ns=_CP_NS, text=resolved.keywords_display)
    sub_element(root, "revision", ns=_CP_NS, text="1")
    created_el = sub_element(root, "created", ns=_DCTERMS_NS, text=_format_timestamp(created))
    created_el.set(ns_tag(_XSI_NS, "type"), "dcterms:W3CDTF")
    modified_el = sub_element(root, "modified", ns=_DCTERMS_NS, text=_format_timestamp(modified))
    modified_el.set(ns_tag(_XSI_NS, "type"), "dcterms:W3CDTF")
    return serialize(root)
