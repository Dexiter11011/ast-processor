"""Validate external YAML theme data and build ThemeTokens."""

from __future__ import annotations

from dataclasses import fields, replace
from typing import Any

from md2docx.sections.definition import PageSize
from md2docx.styles.tokens import (
    ColorTokens,
    HeadingScaleTokens,
    LinkPresentationTokens,
    PageDefaultsTokens,
    SpacingTokens,
    TablePresentationTokens,
    ThemeTokens,
    TypographyTokens,
    default_tokens,
)
from md2docx.themes.errors import ThemeValidationError
from md2docx.themes.units import LengthValue, parse_font_size, parse_length_twips

_TOP_LEVEL_KEYS = frozenset(
    {"name", "typography", "colors", "spacing", "headings", "page", "link", "table"}
)

_TYPOGRAPHY_KEYS = frozenset({"body", "heading", "code"})
_TYPOGRAPHY_BODY_KEYS = frozenset({"family", "size"})
_TYPOGRAPHY_HEADING_KEYS = frozenset({"family"})
_TYPOGRAPHY_CODE_KEYS = frozenset({"family", "size"})

_COLOR_KEYS = frozenset({"text", "heading", "link", "code", "quote"})

_SPACING_KEYS = frozenset(
    {
        "paragraph_after",
        "paragraph_line",
        "paragraph_line_rule",
        "heading1_before",
        "heading1_after",
        "heading2_before",
        "heading2_after",
        "heading3_before",
        "heading3_after",
        "list_indent",
        "toc2_indent",
        "toc3_indent",
        "code_block_after",
        "code_block_line",
        "code_block_line_rule",
    }
)

_HEADING_KEYS = frozenset({"heading1", "heading2", "heading3"})

_PAGE_KEYS = frozenset({"size", "orientation", "emit_margins", "margins"})
_PAGE_MARGIN_KEYS = frozenset({"top", "right", "bottom", "left", "header", "footer"})

_LINK_KEYS = frozenset({"color", "underline"})

_TABLE_KEYS = frozenset(
    {
        "border_sz",
        "border_color_single",
        "border_color_double",
        "cell_margin",
        "header_bold",
        "header_default_align",
    }
)

_PAGE_SIZE_PRESETS = {
    "a4": PageSize.A4,
    "letter": PageSize.LETTER,
}


def _reject_unknown_keys(data: dict[str, Any], allowed: frozenset[str], path: str) -> None:
    for key in data:
        if key not in allowed:
            field_path = f"{path}.{key}" if path else key
            raise ThemeValidationError(field_path, "unknown theme field")


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ThemeValidationError(path, "must be a mapping")
    return value


def _parse_color(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ThemeValidationError(path, "must be a string")
    normalized = value.strip()
    if normalized.startswith("#"):
        normalized = normalized[1:]
    if len(normalized) != 6 or not all(ch in "0123456789abcdefABCDEF" for ch in normalized):
        raise ThemeValidationError(path, "must be a 6-digit hex color")
    return normalized.upper()


def _merge_dataclass(instance: Any, overrides: dict[str, Any]) -> Any:
    allowed = {field.name for field in fields(instance)}
    unknown = set(overrides) - allowed
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ThemeValidationError("", f"unknown internal field(s): {joined}")
    return replace(instance, **overrides)


def _parse_typography(data: dict[str, Any], base: TypographyTokens) -> TypographyTokens:
    _reject_unknown_keys(data, _TYPOGRAPHY_KEYS, "typography")
    overrides: dict[str, Any] = {}

    if "body" in data:
        body = _require_mapping(data["body"], "typography.body")
        _reject_unknown_keys(body, _TYPOGRAPHY_BODY_KEYS, "typography.body")
        if "family" in body:
            family = body["family"]
            if not isinstance(family, str) or not family.strip():
                raise ThemeValidationError("typography.body.family", "must be a non-empty string")
            overrides["body_font_family"] = family.strip()
        if "size" in body:
            overrides["body_font_size"] = parse_font_size(body["size"], path="typography.body.size")

    if "heading" in data:
        heading = _require_mapping(data["heading"], "typography.heading")
        _reject_unknown_keys(heading, _TYPOGRAPHY_HEADING_KEYS, "typography.heading")
        if "family" in heading:
            family = heading["family"]
            if not isinstance(family, str) or not family.strip():
                raise ThemeValidationError("typography.heading.family", "must be a non-empty string")
            overrides["heading_font_family"] = family.strip()

    if "code" in data:
        code = _require_mapping(data["code"], "typography.code")
        _reject_unknown_keys(code, _TYPOGRAPHY_CODE_KEYS, "typography.code")
        if "family" in code:
            family = code["family"]
            if not isinstance(family, str) or not family.strip():
                raise ThemeValidationError("typography.code.family", "must be a non-empty string")
            family = family.strip()
            overrides["code_block_font_family"] = family
            overrides["inline_code_font_family"] = family
        if "size" in code:
            overrides["code_font_size"] = parse_font_size(code["size"], path="typography.code.size")

    return _merge_dataclass(base, overrides) if overrides else base


def _parse_colors(data: dict[str, Any], base: ColorTokens) -> ColorTokens:
    _reject_unknown_keys(data, _COLOR_KEYS, "colors")
    overrides: dict[str, Any] = {}
    for key in data:
        overrides[key] = _parse_color(data[key], f"colors.{key}")
    return _merge_dataclass(base, overrides) if overrides else base


def _parse_spacing(data: dict[str, Any], base: SpacingTokens) -> SpacingTokens:
    _reject_unknown_keys(data, _SPACING_KEYS, "spacing")
    overrides: dict[str, Any] = {}
    for key, value in data.items():
        path = f"spacing.{key}"
        if key.endswith("_rule"):
            if not isinstance(value, str) or not value.strip():
                raise ThemeValidationError(path, "must be a non-empty string")
            internal_key = key
            overrides[internal_key] = value.strip()
            continue
        internal_key = "list_indent_left" if key == "list_indent" else key
        overrides[internal_key] = parse_length_twips(value, path=path)
    return _merge_dataclass(base, overrides) if overrides else base


def _parse_headings(data: dict[str, Any], base: HeadingScaleTokens) -> HeadingScaleTokens:
    _reject_unknown_keys(data, _HEADING_KEYS, "headings")
    mapping = {
        "heading1": "heading1_size",
        "heading2": "heading2_size",
        "heading3": "heading3_size",
    }
    overrides: dict[str, Any] = {}
    for key, internal_key in mapping.items():
        if key not in data:
            continue
        overrides[internal_key] = parse_font_size(data[key], path=f"headings.{key}")
    return _merge_dataclass(base, overrides) if overrides else base


def _parse_page_size(value: Any, path: str) -> tuple[int, int]:
    if isinstance(value, str):
        preset = _PAGE_SIZE_PRESETS.get(value.strip().lower())
        if preset is None:
            raise ThemeValidationError(path, "must be A4, Letter, or a mapping with width and height")
        return preset.width, preset.height
    mapping = _require_mapping(value, path)
    _reject_unknown_keys(mapping, frozenset({"width", "height"}), path)
    if "width" not in mapping or "height" not in mapping:
        raise ThemeValidationError(path, "must include width and height")
    width = parse_length_twips(mapping["width"], path=f"{path}.width")
    height = parse_length_twips(mapping["height"], path=f"{path}.height")
    if width <= 0 or height <= 0:
        raise ThemeValidationError(path, "width and height must be greater than zero")
    return width, height


def _parse_page(data: dict[str, Any], base: PageDefaultsTokens) -> PageDefaultsTokens:
    _reject_unknown_keys(data, _PAGE_KEYS, "page")
    overrides: dict[str, Any] = {}

    if "size" in data:
        width, height = _parse_page_size(data["size"], "page.size")
        overrides["page_width"] = width
        overrides["page_height"] = height

    if "orientation" in data:
        orientation = data["orientation"]
        if not isinstance(orientation, str):
            raise ThemeValidationError("page.orientation", "must be a string")
        normalized = orientation.strip().lower()
        if normalized not in {"portrait", "landscape"}:
            raise ThemeValidationError("page.orientation", "must be portrait or landscape")
        overrides["orientation"] = normalized

    if "emit_margins" in data:
        emit = data["emit_margins"]
        if not isinstance(emit, bool):
            raise ThemeValidationError("page.emit_margins", "must be a boolean")
        overrides["emit_margins"] = emit

    if "margins" in data:
        margins = _require_mapping(data["margins"], "page.margins")
        _reject_unknown_keys(margins, _PAGE_MARGIN_KEYS, "page.margins")
        margin_map = {
            "top": "margin_top",
            "right": "margin_right",
            "bottom": "margin_bottom",
            "left": "margin_left",
            "header": "margin_header",
            "footer": "margin_footer",
        }
        for key, internal_key in margin_map.items():
            if key in margins:
                overrides[internal_key] = parse_length_twips(margins[key], path=f"page.margins.{key}")
        overrides.setdefault("emit_margins", True)

    return _merge_dataclass(base, overrides) if overrides else base


def _parse_link(data: dict[str, Any], base: LinkPresentationTokens) -> LinkPresentationTokens:
    _reject_unknown_keys(data, _LINK_KEYS, "link")
    overrides: dict[str, Any] = {}
    if "color" in data:
        overrides["color"] = _parse_color(data["color"], "link.color")
    if "underline" in data:
        underline = data["underline"]
        if not isinstance(underline, str) or not underline.strip():
            raise ThemeValidationError("link.underline", "must be a non-empty string")
        overrides["underline"] = underline.strip()
    return _merge_dataclass(base, overrides) if overrides else base


def _parse_table(data: dict[str, Any], base: TablePresentationTokens) -> TablePresentationTokens:
    _reject_unknown_keys(data, _TABLE_KEYS, "table")
    overrides: dict[str, Any] = {}
    for key, value in data.items():
        path = f"table.{key}"
        if key == "header_bold":
            if not isinstance(value, bool):
                raise ThemeValidationError(path, "must be a boolean")
            overrides[key] = value
            continue
        if key == "header_default_align":
            if not isinstance(value, str) or not value.strip():
                raise ThemeValidationError(path, "must be a non-empty string")
            overrides[key] = value.strip()
            continue
        if not isinstance(value, str) or not value.strip():
            raise ThemeValidationError(path, "must be a non-empty string")
        overrides[key] = value.strip()
    return _merge_dataclass(base, overrides) if overrides else base


def parse_theme_data(data: Any) -> tuple[str, ThemeTokens]:
    """Validate raw parsed YAML and return theme name plus merged tokens."""
    if not isinstance(data, dict):
        raise ThemeValidationError("", "theme root must be a mapping")

    _reject_unknown_keys(data, _TOP_LEVEL_KEYS, "")

    name = "unnamed"
    if "name" in data:
        raw_name = data["name"]
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ThemeValidationError("name", "must be a non-empty string")
        name = raw_name.strip()

    base = default_tokens()
    typography = base.typography
    colors = base.colors
    spacing = base.spacing
    headings = base.headings
    page = base.page
    link = base.link
    table = base.table

    if "typography" in data:
        typography = _parse_typography(_require_mapping(data["typography"], "typography"), typography)
    if "colors" in data:
        colors = _parse_colors(_require_mapping(data["colors"], "colors"), colors)
    if "spacing" in data:
        spacing = _parse_spacing(_require_mapping(data["spacing"], "spacing"), spacing)
    if "headings" in data:
        headings = _parse_headings(_require_mapping(data["headings"], "headings"), headings)
    if "page" in data:
        page = _parse_page(_require_mapping(data["page"], "page"), page)
    if "link" in data:
        link = _parse_link(_require_mapping(data["link"], "link"), link)
    if "table" in data:
        table = _parse_table(_require_mapping(data["table"], "table"), table)

    tokens = base.override(
        typography=typography,
        colors=colors,
        spacing=spacing,
        headings=headings,
        page=page,
        link=link,
        table=table,
    )
    return name, tokens
