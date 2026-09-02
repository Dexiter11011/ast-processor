"""Validation helpers for namespaced plugin identifiers."""

from __future__ import annotations

import re

from md2docx.plugin_api.errors import InvalidPluginNameError, ReservedNameError

PLUGIN_NAME_RE = re.compile(r"^[a-z][a-z0-9_.]*$")
AST_TYPE_RE = re.compile(r"^[a-z][a-z0-9_.]+$")
PLACEHOLDER_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
STYLE_ID_RE = re.compile(r"^[a-z][a-z0-9_.]+$")

RESERVED_AST_TYPES = frozenset(
    {
        "paragraph",
        "heading",
        "text",
        "strong",
        "emphasis",
        "strikethrough",
        "line_break",
        "footnote_reference",
        "inline_code",
        "link",
        "list",
        "list_item",
        "blockquote",
        "horizontal_rule",
        "page_break",
        "section_break",
        "header_directive",
        "footer_directive",
        "field_directive",
        "figure",
        "table_with_caption",
        "cross_reference",
        "table_of_contents",
        "list_of_figures",
        "list_of_tables",
        "code_block",
        "definition_list",
        "image",
        "table",
        "table_row",
        "table_cell",
    }
)

RESERVED_PLACEHOLDER_NAMES = frozenset(
    {
        "content",
        "title",
        "author",
        "date",
        "subject",
        "keywords",
        "toc",
        "list_of_figures",
        "list_of_tables",
    }
)


def validate_plugin_name(name: str) -> None:
    if not name or not name.strip():
        raise InvalidPluginNameError("plugin name must not be empty")
    if not PLUGIN_NAME_RE.match(name):
        raise InvalidPluginNameError(
            f'invalid plugin name {name!r}; expected lowercase dotted identifier'
        )


def validate_ast_type(type_name: str, *, plugin_name: str) -> None:
    if not type_name or not AST_TYPE_RE.match(type_name):
        raise InvalidPluginNameError(f"invalid AST type name: {type_name!r}")
    if type_name in RESERVED_AST_TYPES:
        raise ReservedNameError(f'AST type {type_name!r} is reserved by the core engine')
    if not type_name.startswith(f"{plugin_name}."):
        raise InvalidPluginNameError(
            f'AST type {type_name!r} must be namespaced under plugin {plugin_name!r}'
        )


def validate_placeholder_name(name: str) -> None:
    if not name or not PLACEHOLDER_NAME_RE.match(name):
        raise InvalidPluginNameError(f"invalid template region name: {name!r}")
    if name in RESERVED_PLACEHOLDER_NAMES:
        raise ReservedNameError(f'template region {name!r} is reserved by the core engine')


def validate_style_id(semantic_id: str, *, plugin_name: str) -> None:
    if not semantic_id or not STYLE_ID_RE.match(semantic_id):
        raise InvalidPluginNameError(f"invalid style semantic id: {semantic_id!r}")
    prefix = plugin_name.replace(".", "_")
    if not semantic_id.startswith(f"{prefix}.") and not semantic_id.startswith(f"{plugin_name}."):
        raise InvalidPluginNameError(
            f'style {semantic_id!r} must be namespaced under plugin {plugin_name!r}'
        )
