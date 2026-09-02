"""Validate and apply template placeholders before content insertion."""

from __future__ import annotations

from lxml import etree

from md2docx.templates.composition import (
    build_navigation_fragments,
    build_plugin_fragments,
    navigation_region_names,
    plugin_region_names,
)
from md2docx.templates.composition_plan import TemplateCompositionPlan
from md2docx.templates.context import DocumentContext
from md2docx.templates.errors import TemplateInsertionError, TemplatePlaceholderError
from md2docx.templates.insertion import insert_fragment_at_index
from md2docx.ooxml.xml_builder import w_tag
from md2docx.templates.placeholder_scan import scan_body_placeholders
from md2docx.templates.placeholders import PlaceholderKind, TemplatePlaceholder
from md2docx.templates.scalar_replace import replace_scalar_placeholder

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from md2docx.processor.context import ProcessingContext
    from md2docx.plugin_api.registry import PluginRegistry


class TemplateComposer:
    """Scan, validate, and apply template placeholders in document.xml."""

    @staticmethod
    def validate_placeholders(
        placeholders: list[TemplatePlaceholder],
        document_context: DocumentContext,
    ) -> None:
        content_placeholders = [item for item in placeholders if item.kind is PlaceholderKind.CONTENT]
        if len(content_placeholders) == 0:
            raise TemplateInsertionError('template insertion point "{{content}}" was not found')
        if len(content_placeholders) > 1:
            raise TemplateInsertionError(
                "template contains multiple {{content}} insertion points"
            )

        required_scalars = {
            item.name
            for item in placeholders
            if item.kind is PlaceholderKind.SCALAR
        }
        for name in sorted(required_scalars):
            value = document_context.get(name)
            if value is None:
                raise TemplatePlaceholderError(
                    f'missing value for template placeholder "{{{{{name}}}}}"'
                )

    @staticmethod
    def apply_scalar_placeholders(
        document_xml: bytes,
        placeholders: list[TemplatePlaceholder],
        document_context: DocumentContext,
    ) -> bytes:
        scalar_items = [item for item in placeholders if item.kind is PlaceholderKind.SCALAR]
        if not scalar_items:
            return document_xml

        root = etree.fromstring(document_xml)
        body = root.find(w_tag("body"))
        if body is None:
            raise TemplateInsertionError("template document.xml has no w:body")
        paragraphs = [child for child in body if etree.QName(child).localname == "p"]

        for placeholder in scalar_items:
            if placeholder.paragraph_index >= len(paragraphs):
                raise TemplatePlaceholderError(
                    f'template placeholder "{{{{{placeholder.name}}}}}" paragraph index out of range'
                )
            value = document_context.get(placeholder.name)
            if value is None:
                raise TemplatePlaceholderError(
                    f'missing value for template placeholder "{{{{{placeholder.name}}}}}"'
                )
            replace_scalar_placeholder(paragraphs[placeholder.paragraph_index], placeholder, value)

        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    @staticmethod
    def compose_document(
        document_xml: bytes,
        fragment_children: list[etree._Element],
        document_context: DocumentContext,
        *,
        processing_context: ProcessingContext | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> bytes:
        plugin_kinds = plugin_registry.plugin_placeholder_kinds() if plugin_registry else None
        placeholders = scan_body_placeholders(document_xml, extra_placeholders=plugin_kinds)
        TemplateComposer.validate_placeholders(placeholders, document_context)
        document_xml = TemplateComposer.apply_scalar_placeholders(
            document_xml,
            placeholders,
            document_context,
        )

        nav_names = navigation_region_names(placeholders)
        nav_fragments: dict[str, list[etree._Element]] = {}
        if nav_names:
            if processing_context is None:
                raise TemplateInsertionError(
                    "template navigation regions require a processing context"
                )
            nav_fragments = build_navigation_fragments(processing_context, nav_names)

        plugin_names = plugin_region_names(placeholders)
        plugin_fragments: dict[str, list[etree._Element]] = {}
        if plugin_names:
            if processing_context is None or plugin_registry is None:
                raise TemplateInsertionError(
                    "plugin template regions require a processing context and plugin registry"
                )
            plugin_fragments = build_plugin_fragments(
                processing_context,
                plugin_registry,
                plugin_names,
            )

        plan = TemplateCompositionPlan(
            content_fragment=fragment_children,
            navigation_fragments=nav_fragments,
            plugin_fragments=plugin_fragments,
        )
        return TemplateComposer.compose_with_plan(document_xml, placeholders, plan)

    @staticmethod
    def compose_with_plan(
        document_xml: bytes,
        placeholders: list[TemplatePlaceholder],
        plan: TemplateCompositionPlan,
    ) -> bytes:
        fragment_items = plan.fragment_placeholders(placeholders)
        for placeholder in sorted(fragment_items, key=lambda item: item.paragraph_index, reverse=True):
            children = plan.fragment_for(placeholder)
            document_xml = insert_fragment_at_index(
                document_xml,
                placeholder.paragraph_index,
                children,
            )
        return document_xml
