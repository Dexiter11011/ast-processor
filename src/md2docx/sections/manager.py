"""Document-level section and page layout manager."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from lxml import etree

from md2docx.ooxml.header_footer import build_footer_part, build_header_part
from md2docx.ooxml.relationships import FOOTER_REL_TYPE, HEADER_REL_TYPE, RelationshipManager
from md2docx.ooxml.section import attach_sect_pr_to_paragraph, build_sect_pr
from md2docx.ooxml.xml_builder import W_NS, w_tag
from md2docx.sections.definition import PageLayout, Section


@dataclass
class HeaderFooterPart:
    part_path: str
    rel_id: str
    xml: bytes


@dataclass
class SectionManager:
    """Owns sections, page layout, and header/footer parts."""

    relationships: RelationshipManager
    default_layout: PageLayout | None = None
    _sections: list[Section] = field(default_factory=list)
    _header_parts: list[HeaderFooterPart] = field(default_factory=list)
    _footer_parts: list[HeaderFooterPart] = field(default_factory=list)
    _next_header_index: int = 1
    _next_footer_index: int = 1

    def __post_init__(self) -> None:
        if not self._sections:
            layout = self.default_layout or PageLayout.a4_portrait()
            self._sections.append(Section(layout=layout))

    def current_section(self) -> Section:
        return self._sections[-1]

    def add_section(
        self,
        layout: PageLayout | None,
        body_children: list[etree._Element],
    ) -> Section:
        """Close the current section and start a new one."""
        if self._sections:
            self._close_section(self._sections[-1], body_children)
        section = Section(layout=layout or PageLayout.a4_portrait())
        self._sections.append(section)
        return section

    def add_current_header_paragraphs(self, paragraphs: list[etree._Element]) -> str:
        """Append paragraphs to the current section header and rebuild the header part."""
        section = self.current_section()
        section.header_paragraphs.extend(paragraphs)
        rel_id = self._sync_header_part(section)
        section.header_rel_id = rel_id
        return rel_id

    def add_current_footer_paragraphs(self, paragraphs: list[etree._Element]) -> str:
        """Append paragraphs to the current section footer and rebuild the footer part."""
        section = self.current_section()
        section.footer_paragraphs.extend(paragraphs)
        rel_id = self._sync_footer_part(section)
        section.footer_rel_id = rel_id
        return rel_id

    def _close_section(self, section: Section, body_children: list[etree._Element]) -> None:
        sect_pr = build_sect_pr(
            section.layout,
            header_rel_id=section.header_rel_id,
            footer_rel_id=section.footer_rel_id,
        )
        target = self._last_paragraph(body_children)
        if target is None:
            target = etree.Element(w_tag("p"), nsmap={"w": W_NS})
            body_children.append(target)
        attach_sect_pr_to_paragraph(target, sect_pr)

    def _sync_header_part(self, section: Section) -> str:
        xml = build_header_part(section.header_paragraphs)
        return self._upsert_header_part(xml, section.header_rel_id)

    def _sync_footer_part(self, section: Section) -> str:
        xml = build_footer_part(section.footer_paragraphs)
        return self._upsert_footer_part(xml, section.footer_rel_id)

    def _upsert_header_part(self, xml: bytes, existing_rel_id: str | None) -> str:
        if existing_rel_id is not None:
            for part in self._header_parts:
                if part.rel_id == existing_rel_id:
                    part.xml = xml
                    return part.rel_id
        for existing in self._header_parts:
            if existing.xml == xml:
                return existing.rel_id
        part_name = f"header{self._next_header_index}.xml"
        self._next_header_index += 1
        rel_id = self.relationships.add(HEADER_REL_TYPE, part_name)
        self._header_parts.append(
            HeaderFooterPart(part_path=f"word/{part_name}", rel_id=rel_id, xml=xml)
        )
        return rel_id

    def _upsert_footer_part(self, xml: bytes, existing_rel_id: str | None) -> str:
        if existing_rel_id is not None:
            for part in self._footer_parts:
                if part.rel_id == existing_rel_id:
                    part.xml = xml
                    return part.rel_id
        for existing in self._footer_parts:
            if existing.xml == xml:
                return existing.rel_id
        part_name = f"footer{self._next_footer_index}.xml"
        self._next_footer_index += 1
        rel_id = self.relationships.add(FOOTER_REL_TYPE, part_name)
        self._footer_parts.append(
            HeaderFooterPart(part_path=f"word/{part_name}", rel_id=rel_id, xml=xml)
        )
        return rel_id

    def finalize_body(self, body: etree._Element, body_children: list[etree._Element]) -> None:
        """Copy body children and append final sectPr for the last section."""
        for child in body_children:
            body.append(deepcopy(child))
        final = self.current_section()
        body.append(
            build_sect_pr(
                final.layout,
                header_rel_id=final.header_rel_id,
                footer_rel_id=final.footer_rel_id,
            )
        )

    def header_footer_parts(self) -> dict[str, bytes]:
        parts: dict[str, bytes] = {}
        for part in self._header_parts:
            parts[part.part_path] = part.xml
        for part in self._footer_parts:
            parts[part.part_path] = part.xml
        return parts

    def header_part_paths(self) -> list[str]:
        return [part.part_path for part in self._header_parts]

    def footer_part_paths(self) -> list[str]:
        return [part.part_path for part in self._footer_parts]

    @staticmethod
    def _last_paragraph(body_children: list[etree._Element]) -> etree._Element | None:
        for child in reversed(body_children):
            if etree.QName(child).localname == "p":
                return child
        return None
