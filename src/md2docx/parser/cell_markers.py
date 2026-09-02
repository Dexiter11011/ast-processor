"""Parse per-cell markers for shading, alignment, and merge hints."""

from __future__ import annotations

import re
from dataclasses import dataclass

CELL_BG_RE = re.compile(r"^\{bg:([0-9A-Fa-f]{6}|[a-z]+)\}")
CELL_VALIGN_RE = re.compile(r"^\{valign:(top|center|bottom)\}")

_NAMED_COLORS = {
    "yellow": "FFF2CC",
    "green": "E2EFDA",
    "blue": "DDEBF7",
    "red": "FCE4D6",
    "gray": "F2F2F2",
    "grey": "F2F2F2",
    "orange": "FCE4D6",
}


@dataclass(frozen=True)
class ParsedCellContent:
    align: str = ""
    bg: str = ""
    valign: str = ""
    text: str = ""
    vmerge_continue: bool = False


def resolve_fill_color(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in _NAMED_COLORS:
        return _NAMED_COLORS[normalized]
    if len(normalized) == 6 and all(ch in "0123456789abcdef" for ch in normalized):
        return normalized.upper()
    return ""


def parse_gost_cell_align(raw: str) -> tuple[str, str]:
    """Return (align, text) using GOST edge-colon markers."""
    text = raw.strip()
    if not text:
        return "", ""

    if text.startswith(":") and text.endswith(":") and len(text) >= 2:
        return "center", text[1:-1].strip()

    if text.startswith(":"):
        return "left", text[1:].strip()

    if text.endswith(":"):
        return "right", text[:-1].strip()

    return "", text


def parse_cell_content(raw: str) -> ParsedCellContent:
    text = raw.strip()
    if text == "^^":
        return ParsedCellContent(vmerge_continue=True)

    bg = ""
    valign = ""
    align = ""
    changed = True
    while changed:
        changed = False
        bg_match = CELL_BG_RE.match(text)
        if bg_match is not None:
            bg = resolve_fill_color(bg_match.group(1))
            text = text[bg_match.end() :].strip()
            changed = True
            continue
        valign_match = CELL_VALIGN_RE.match(text)
        if valign_match is not None:
            valign = valign_match.group(1)
            text = text[valign_match.end() :].strip()
            changed = True
            continue
        gost_align, gost_text = parse_gost_cell_align(text)
        if gost_align:
            align = gost_align
            text = gost_text
            changed = True
    return ParsedCellContent(align=align, bg=bg, valign=valign, text=text)
