"""AST transforms for navigation blocks and template region deduplication."""

from __future__ import annotations

from md2docx.ast.types import Document


def strip_ast_types_for_template_regions(
    document: Document,
    strip_types: set[str],
) -> Document:
    """Remove AST nodes whose ``type`` values are provided by the template."""
    if not strip_types:
        return document
    filtered = [child for child in document.children if getattr(child, "type", None) not in strip_types]
    return Document(
        children=filtered,
        metadata=document.metadata,
        footnotes=document.footnotes,
    )


def strip_navigation_for_template_regions(document: Document, region_names: set[str]) -> Document:
    """Remove navigation AST nodes when the template provides matching regions."""
    if not region_names:
        return document

    strip_types: set[str] = set()
    if "toc" in region_names:
        strip_types.add("table_of_contents")
    if "list_of_figures" in region_names:
        strip_types.add("list_of_figures")
    if "list_of_tables" in region_names:
        strip_types.add("list_of_tables")

    return strip_ast_types_for_template_regions(document, strip_types)
