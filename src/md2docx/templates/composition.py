"""Document fragment rendering for template navigation regions."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from lxml import etree

from md2docx.templates.placeholders import PlaceholderKind, TemplatePlaceholder
from md2docx.templates.regions import TemplateRegionKind

if TYPE_CHECKING:
    from md2docx.processor.context import ProcessingContext

DEFAULT_TOC_MIN_LEVEL = 1
DEFAULT_TOC_MAX_LEVEL = 3


def navigation_region_names(placeholders: list[TemplatePlaceholder]) -> set[str]:
    return {item.name for item in placeholders if item.kind is PlaceholderKind.NAVIGATION}


def render_navigation_fragment(context: ProcessingContext, name: str) -> list[etree._Element]:
    """Render a navigation region fragment using the existing field stack."""
    from md2docx.toc.definition import TocSpec

    if name == TemplateRegionKind.TOC.value:
        context.fields.mark_dynamic_field_used()
        paragraph = context.toc.build_paragraph(
            TocSpec(min_level=DEFAULT_TOC_MIN_LEVEL, max_level=DEFAULT_TOC_MAX_LEVEL)
        )
        return [deepcopy(paragraph)]
    if name == TemplateRegionKind.LIST_OF_FIGURES.value:
        context.fields.mark_dynamic_field_used()
        return [deepcopy(context.toc.build_lof_paragraph())]
    if name == TemplateRegionKind.LIST_OF_TABLES.value:
        context.fields.mark_dynamic_field_used()
        return [deepcopy(context.toc.build_lot_paragraph())]
    raise ValueError(f"unsupported navigation region: {name}")


def build_navigation_fragments(
    context: ProcessingContext,
    region_names: set[str],
) -> dict[str, list[etree._Element]]:
    """Build navigation fragments for all requested region names."""
    return {name: render_navigation_fragment(context, name) for name in sorted(region_names)}


def plugin_region_names(placeholders: list[TemplatePlaceholder]) -> set[str]:
    return {item.name for item in placeholders if item.kind is PlaceholderKind.PLUGIN}


def build_plugin_fragments(
    context: ProcessingContext,
    plugin_registry,
    region_names: set[str],
) -> dict[str, list[etree._Element]]:
    from copy import deepcopy

    fragments: dict[str, list[etree._Element]] = {}
    for name in sorted(region_names):
        region = plugin_registry.region_for(name)
        if region is None:
            continue
        rendered = region.render_fragment(context)
        from md2docx.semantic.renderer import coerce_template_fragment

        fragments[name] = [deepcopy(child) for child in coerce_template_fragment(rendered, context)]
    return fragments
