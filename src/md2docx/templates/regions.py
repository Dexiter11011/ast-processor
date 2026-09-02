"""Typed template region identifiers."""

from __future__ import annotations

from enum import Enum


class TemplateRegionKind(Enum):
    """Semantic template insertion region kinds."""

    CONTENT = "content"
    TOC = "toc"
    LIST_OF_FIGURES = "list_of_figures"
    LIST_OF_TABLES = "list_of_tables"


REGION_KIND_BY_NAME: dict[str, TemplateRegionKind] = {
    TemplateRegionKind.CONTENT.value: TemplateRegionKind.CONTENT,
    TemplateRegionKind.TOC.value: TemplateRegionKind.TOC,
    TemplateRegionKind.LIST_OF_FIGURES.value: TemplateRegionKind.LIST_OF_FIGURES,
    TemplateRegionKind.LIST_OF_TABLES.value: TemplateRegionKind.LIST_OF_TABLES,
}


def region_kind_for_name(name: str) -> TemplateRegionKind | None:
    """Return typed region kind for a normalized placeholder name."""
    return REGION_KIND_BY_NAME.get(name)
