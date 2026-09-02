"""DOCX package writer (ZIP assembly)."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Union

from md2docx.output.atomic import AtomicOutputWriter

OutputDestination = Union[Path, AtomicOutputWriter]

from lxml import etree

from md2docx.ooxml.app_props import build_app_props_xml
from md2docx.ooxml.content_types import build_content_types_xml
from md2docx.ooxml.core_props import build_core_props_xml
from md2docx.ooxml.document import OoxmlDocument
from md2docx.ooxml.footnote import build_footnotes_xml
from md2docx.ooxml.numbering import NumberingManager
from md2docx.ooxml.relationships import FOOTNOTES_REL_TYPE, NUMBERING_REL_TYPE, RelationshipManager, SETTINGS_REL_TYPE
from md2docx.ooxml.settings import SETTINGS_PART, DocumentSettings, build_settings_xml
from md2docx.ooxml.styles import build_minimal_styles_xml
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag

if TYPE_CHECKING:
    from md2docx.ast.metadata import DocumentMetadata
    from md2docx.metadata.resolved import ResolvedDocumentMetadata
    from md2docx.processor.context import MediaManager, ProcessingContext
    from md2docx.sections.manager import SectionManager

    MetadataInput = ResolvedDocumentMetadata | DocumentMetadata
else:
    from md2docx.ast.metadata import DocumentMetadata

    MetadataInput = object


class DocxPackageWriter:
    """Write a minimal valid DOCX from an OoxmlDocument."""

    def write_from_context(
        self,
        context: ProcessingContext,
        output_path: OutputDestination,
        *,
        metadata: MetadataInput | None = None,
        update_fields: bool | None = None,
    ) -> None:
        """Write a DOCX using all shared resources from *context*."""
        settings = DocumentSettings(
            update_fields_on_open=(
                update_fields
                if update_fields is not None
                else context.fields.has_dynamic_fields
            )
        )
        self.write(
            context.document,
            output_path,
            relationships=context.relationships,
            numbering=context.numbering,
            media=context.media,
            sections=context.sections,
            metadata=metadata,
            styles_xml=context.styles.styles_xml(),
            document_settings=settings,
            footnote_bodies=(
                context.footnotes.footnote_paragraphs() if context.footnotes.has_footnotes else None
            ),
        )

    def write(
        self,
        document: OoxmlDocument,
        output_path: OutputDestination,
        *,
        relationships: RelationshipManager | None = None,
        numbering: NumberingManager | None = None,
        media: MediaManager | None = None,
        sections: SectionManager | None = None,
        metadata: MetadataInput | None = None,
        styles_xml: bytes | None = None,
        document_settings: DocumentSettings | None = None,
        footnote_bodies: dict[int, list[etree._Element]] | None = None,
    ) -> None:
        if isinstance(output_path, Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        rels = relationships or RelationshipManager()
        if not rels.relationships:
            rels.add_styles_relationship()

        numbering_xml = numbering.to_bytes() if numbering else None
        if numbering_xml and not any(r.rel_type == NUMBERING_REL_TYPE for r in rels.relationships):
            rels.add_numbering_relationship()

        settings = document_settings or DocumentSettings()
        include_settings = settings.update_fields_on_open
        if include_settings and not any(r.rel_type == SETTINGS_REL_TYPE for r in rels.relationships):
            rels.add_settings_relationship()

        footnotes_xml: bytes | None = None
        if footnote_bodies:
            footnotes_xml = build_footnotes_xml(footnote_bodies)
            if not any(r.rel_type == FOOTNOTES_REL_TYPE for r in rels.relationships):
                rels.add_footnotes_relationship()

        media_parts = media.parts if media else {}
        media_extensions = {Path(path).suffix.lstrip(".").lower() for path in media_parts if "." in path}
        include_doc_props = metadata is not None and metadata.has_values()

        body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
        if sections is not None:
            sections.finalize_body(body, document.body_children)
        else:
            from copy import deepcopy

            for child in document.body_children:
                body.append(deepcopy(child))
            sect_pr = etree.SubElement(body, w_tag("sectPr"))
            pg_sz = etree.SubElement(sect_pr, w_tag("pgSz"))
            pg_sz.set(w_tag("w"), "11906")
            pg_sz.set(w_tag("h"), "16838")

        doc_root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
        doc_root.append(body)
        doc_xml = serialize(doc_root)

        header_paths = sections.header_part_paths() if sections else []
        footer_paths = sections.footer_part_paths() if sections else []
        header_footer_parts = sections.header_footer_parts() if sections else {}

        parts: dict[str, bytes] = {
            "[Content_Types].xml": build_content_types_xml(
                has_numbering=numbering_xml is not None,
                has_footnotes=footnotes_xml is not None,
                has_doc_props=include_doc_props,
                has_settings=include_settings,
                media_extensions=media_extensions,
                header_parts=header_paths,
                footer_parts=footer_paths,
            ),
            "_rels/.rels": rels.build_root_rels_xml(include_doc_props=include_doc_props),
            "word/document.xml": doc_xml,
            "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
            "word/styles.xml": styles_xml or build_minimal_styles_xml(),
        }
        if numbering_xml:
            parts["word/numbering.xml"] = numbering_xml
        if footnotes_xml is not None:
            parts["word/footnotes.xml"] = footnotes_xml
        if include_doc_props and metadata is not None:
            parts["docProps/core.xml"] = build_core_props_xml(metadata)
            parts["docProps/app.xml"] = build_app_props_xml()
        if include_settings:
            parts[SETTINGS_PART] = build_settings_xml(settings)
        parts.update(header_footer_parts)
        parts.update(media_parts)
        self._write_zip(output_path, parts)

    def write_package(self, parts: dict[str, bytes], output_path: OutputDestination) -> None:
        """Write a pre-assembled DOCX package to disk."""
        if isinstance(output_path, Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_zip(output_path, parts)

    def _write_zip(self, destination: OutputDestination, parts: dict[str, bytes]) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name in sorted(parts):
                zf.writestr(name, parts[name])
        data = buf.getvalue()
        if isinstance(destination, AtomicOutputWriter):
            destination.write_bytes(data)
        else:
            destination.write_bytes(data)
