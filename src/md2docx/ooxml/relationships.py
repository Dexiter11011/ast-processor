"""Relationship ID management for OOXML package."""

from __future__ import annotations

from dataclasses import dataclass, field

from lxml import etree

from md2docx.ooxml.xml_builder import PKG_NS, ns_tag, serialize, sub_element

HEADER_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
FOOTER_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
STYLES_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"
HYPERLINK_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
IMAGE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
NUMBERING_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering"
SETTINGS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings"
FOOTNOTES_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"
CORE_PROPS_REL_TYPE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
APP_PROPS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
OFFICE_DOCUMENT_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"


@dataclass
class Relationship:
    rel_id: str
    rel_type: str
    target: str
    target_mode: str = ""


@dataclass
class RelationshipManager:
    """Centralized relationship ID allocation."""

    _next_id: int = 1
    relationships: list[Relationship] = field(default_factory=list)
    _hyperlink_urls: dict[str, str] = field(default_factory=dict)

    def add(self, rel_type: str, target: str, *, target_mode: str = "") -> str:
        rel_id = f"rId{self._next_id}"
        self._next_id += 1
        self.relationships.append(
            Relationship(rel_id=rel_id, rel_type=rel_type, target=target, target_mode=target_mode)
        )
        return rel_id

    def add_styles_relationship(self) -> str:
        return self.add(STYLES_REL_TYPE, "styles.xml")

    def add_numbering_relationship(self) -> str:
        return self.add(NUMBERING_REL_TYPE, "numbering.xml")

    def add_settings_relationship(self) -> str:
        return self.add(SETTINGS_REL_TYPE, "settings.xml")

    def add_footnotes_relationship(self) -> str:
        return self.add(FOOTNOTES_REL_TYPE, "footnotes.xml")

    def add_external_hyperlink(self, url: str) -> str:
        if url in self._hyperlink_urls:
            return self._hyperlink_urls[url]
        rel_id = self.add(HYPERLINK_REL_TYPE, url, target_mode="External")
        self._hyperlink_urls[url] = rel_id
        return rel_id

    def add_image_relationship(self, media_filename: str) -> str:
        return self.add(IMAGE_REL_TYPE, f"media/{media_filename}")

    def add_header_relationship(self, part_name: str) -> str:
        return self.add(HEADER_REL_TYPE, part_name)

    def add_footer_relationship(self, part_name: str) -> str:
        return self.add(FOOTER_REL_TYPE, part_name)

    def build_document_rels_xml(self) -> bytes:
        root = etree.Element(ns_tag(PKG_NS, "Relationships"), nsmap={None: PKG_NS})
        for rel in self.relationships:
            attrs = {"Id": rel.rel_id, "Type": rel.rel_type, "Target": rel.target}
            if rel.target_mode:
                attrs["TargetMode"] = rel.target_mode
            sub_element(root, "Relationship", attrs=attrs)
        return serialize(root)

    def build_root_rels_xml(self, *, include_doc_props: bool = False) -> bytes:
        root = etree.Element(ns_tag(PKG_NS, "Relationships"), nsmap={None: PKG_NS})
        sub_element(
            root,
            "Relationship",
            attrs={
                "Id": "rId1",
                "Type": OFFICE_DOCUMENT_REL_TYPE,
                "Target": "word/document.xml",
            },
        )
        if include_doc_props:
            sub_element(
                root,
                "Relationship",
                attrs={
                    "Id": "rId2",
                    "Type": CORE_PROPS_REL_TYPE,
                    "Target": "docProps/core.xml",
                },
            )
            sub_element(
                root,
                "Relationship",
                attrs={
                    "Id": "rId3",
                    "Type": APP_PROPS_REL_TYPE,
                    "Target": "docProps/app.xml",
                },
            )
        return serialize(root)
