"""Orchestrate merging generated Markdown content into a DOCX template."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from md2docx.ooxml.app_props import build_app_props_xml
from md2docx.ooxml.content_types import _EXT_TO_CT
from md2docx.ooxml.core_props import build_core_props_xml
from md2docx.processor.context import ProcessingContext
from md2docx.styles import semantic as S
from md2docx.styles.ooxml_ids import SEMANTIC_TO_OOXML
from md2docx.styles.theme import DocumentTheme
from md2docx.templates.bookmark_remap import collect_bookmark_names, remap_bookmarks
from md2docx.templates.composer import TemplateComposer
from md2docx.templates.content_types_merge import merge_content_types
from md2docx.templates.context import DocumentContext
from md2docx.templates.docprops_merge import ensure_docprops_package_parts
from md2docx.templates.errors import TemplateLoadError, TemplateMergeError
from md2docx.templates.insertion import max_bookmark_id
from md2docx.templates.footnote_remap import (
    max_footnote_id,
    merge_footnotes_xml,
    remap_footnote_bodies,
    remap_footnote_ids,
)
from md2docx.templates.numbering_remap import merge_numbering
from md2docx.templates.package import (
    CONTENT_TYPES_PART,
    DOCUMENT_PART,
    DOCUMENT_RELS_PART,
    FOOTNOTES_PART,
    NUMBERING_PART,
    STYLES_PART,
    TemplatePackage,
)
from md2docx.templates.relationship_remap import (
    merge_document_relationships,
    resolve_media_collisions,
    rewrite_relationship_ids,
)
from md2docx.templates.settings_merge import ensure_settings_package_parts
from md2docx.templates.style_merge import merge_template_and_theme_styles, template_style_ids

REQUIRED_TEMPLATE_STYLE_IDS = frozenset(
    ooxml_id
    for semantic_id, ooxml_id in SEMANTIC_TO_OOXML.items()
    if semantic_id
    not in (
        S.CAPTION,
        S.FOOTNOTE_TEXT,
        S.DEFINITION_TERM,
        S.DEFINITION_DESCRIPTION,
    )
)


class TemplateMerger:
    """Merge generated document content into a loaded template package."""

    @staticmethod
    def validate_template_styles(template: TemplatePackage) -> None:
        present = template_style_ids(template.get_part(STYLES_PART))
        missing = sorted(REQUIRED_TEMPLATE_STYLE_IDS - present)
        if missing:
            joined = ", ".join(missing)
            raise TemplateLoadError(f"template is missing required styles: {joined}")

    @staticmethod
    def merge(
        template: TemplatePackage,
        context: ProcessingContext,
        *,
        theme: DocumentTheme | None = None,
        document_context: DocumentContext | None = None,
        resolved_metadata=None,
        update_fields: bool | None = None,
        plugin_registry=None,
    ) -> dict[str, bytes]:
        TemplateMerger.validate_template_styles(template)
        parts = template.copy_parts()
        active_context = document_context or DocumentContext()

        if theme is not None:
            parts[STYLES_PART] = merge_template_and_theme_styles(
                parts[STYLES_PART],
                context.styles.styles_xml(),
            )

        fragment = [deepcopy(child) for child in context.document.body_children]
        template_had_numbering = template.has_part(NUMBERING_PART)
        generated_numbering = context.numbering.to_bytes()
        fragment, numbering_xml, add_numbering_rel = merge_numbering(
            parts.get(NUMBERING_PART),
            generated_numbering,
            fragment,
        )
        if numbering_xml is not None:
            parts[NUMBERING_PART] = numbering_xml

        media_parts, media_target_map = resolve_media_collisions(parts, context.media.parts)
        parts.update(media_parts)

        document_rels, rel_id_map = merge_document_relationships(
            parts[DOCUMENT_RELS_PART],
            context.relationships.relationships,
            media_target_map=media_target_map,
            add_numbering_relationship=add_numbering_rel and not template_had_numbering,
        )
        parts[DOCUMENT_RELS_PART] = document_rels
        fragment = rewrite_relationship_ids(fragment, rel_id_map)

        bookmark_start = max_bookmark_id(parts[DOCUMENT_PART]) + 1
        if bookmark_start <= 0:
            bookmark_start = 0
        template_bookmark_names = collect_bookmark_names(parts[DOCUMENT_PART])
        fragment, _remap = remap_bookmarks(
            fragment,
            start_id=bookmark_start,
            reserved_names=template_bookmark_names,
        )

        add_footnotes = False
        if context.footnotes.has_footnotes:
            template_footnotes = parts.get(FOOTNOTES_PART)
            start_footnote_id = max_footnote_id(template_footnotes) + 1 if template_footnotes else 1
            fragment, footnote_remap = remap_footnote_ids(fragment, start_id=start_footnote_id)
            remapped_bodies = remap_footnote_bodies(
                context.footnotes.footnote_paragraphs(),
                footnote_remap,
            )
            parts[FOOTNOTES_PART] = merge_footnotes_xml(template_footnotes, remapped_bodies)
            add_footnotes = template_footnotes is None

        parts[DOCUMENT_PART] = TemplateComposer.compose_document(
            parts[DOCUMENT_PART],
            fragment,
            active_context,
            processing_context=context,
            plugin_registry=plugin_registry,
        )

        media_extensions = {
            Path(path).suffix.lstrip(".").lower()
            for path in media_parts
            if Path(path).suffix
        }
        media_extensions = {ext for ext in media_extensions if ext in _EXT_TO_CT}
        add_doc_props = active_context.has_core_props_values()
        parts[CONTENT_TYPES_PART] = merge_content_types(
            parts[CONTENT_TYPES_PART],
            media_extensions=media_extensions,
            add_numbering=NUMBERING_PART in parts and not template_had_numbering,
            add_doc_props=add_doc_props,
            add_footnotes=add_footnotes,
        )

        if add_doc_props:
            from md2docx.metadata.resolved import ResolvedDocumentMetadata

            metadata = resolved_metadata
            if metadata is None:
                metadata = ResolvedDocumentMetadata(
                    title=active_context.title,
                    author=active_context.author,
                    date=active_context.date,
                    subject=active_context.subject,
                    keywords=tuple(
                        part.strip()
                        for part in (active_context.keywords or "").split(",")
                        if part.strip()
                    ),
                )
            parts["docProps/core.xml"] = build_core_props_xml(metadata)
            parts["docProps/app.xml"] = build_app_props_xml()
            ensure_docprops_package_parts(parts)

        should_update_fields = (
            update_fields
            if update_fields is not None
            else context.fields.has_dynamic_fields
        )
        ensure_settings_package_parts(parts, update_fields_on_open=should_update_fields)

        if not parts.get(DOCUMENT_PART):
            raise TemplateMergeError("merged template document.xml is empty")

        return parts
