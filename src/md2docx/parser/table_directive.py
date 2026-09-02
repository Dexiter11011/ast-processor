"""Parse optional HTML table directives above GFM tables."""

from __future__ import annotations

import re

TABLE_DIRECTIVE_RE = re.compile(r"<!--\s*table:\s*(.+?)\s*-->")


def is_table_directive_text(text: str) -> bool:
    return TABLE_DIRECTIVE_RE.match(text.strip()) is not None


def parse_table_directive(source: str, line_no: int | None) -> dict[str, str]:
    if line_no is None or line_no <= 0:
        return {}
    lines = source.splitlines()
    if line_no - 1 >= len(lines):
        return {}
    match = TABLE_DIRECTIVE_RE.match(lines[line_no - 1].strip())
    if match is None:
        return {}
    attrs: dict[str, str] = {}
    for part in match.group(1).split():
        if "=" in part:
            key, value = part.split("=", 1)
            attrs[key.strip()] = value.strip()
    return attrs


def parse_cell_align(attrs: dict | None) -> str:
    if not attrs:
        return ""
    style = attrs.get("style", "")
    if style.startswith("text-align:"):
        return style.split(":", 1)[1].strip()
    return ""
