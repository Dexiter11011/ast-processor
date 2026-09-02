"""User-friendly measurement parsing for external themes."""

from __future__ import annotations

import re
from typing import Union

from md2docx.themes.errors import ThemeValidationError

LengthValue = Union[int, float, str]

_PT_TO_TWIPS = 20
_PT_TO_HALF_POINTS = 2

_LENGTH_RE = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*(pt|in|cm|mm|twips?)?\s*$",
    re.IGNORECASE,
)


def parse_font_size(value: LengthValue, *, path: str) -> int:
    """Parse a font size into Word half-points (22 = 11pt)."""
    if isinstance(value, bool):
        raise ThemeValidationError(path, "must be a number or length")
    if isinstance(value, (int, float)):
        if value <= 0:
            raise ThemeValidationError(path, "must be greater than zero")
        return int(round(float(value) * _PT_TO_HALF_POINTS))
    if isinstance(value, str):
        match = _LENGTH_RE.match(value)
        if not match:
            raise ThemeValidationError(path, "must be a number or length such as 11pt")
        amount = float(match.group(1))
        unit = (match.group(2) or "pt").lower()
        if unit != "pt":
            raise ThemeValidationError(path, "font size must use pt units")
        if amount <= 0:
            raise ThemeValidationError(path, "must be greater than zero")
        return int(round(amount * _PT_TO_HALF_POINTS))
    raise ThemeValidationError(path, "must be a number or length")


def parse_length_twips(value: LengthValue, *, path: str) -> int:
    """Parse spacing, indent, or margin values into twips."""
    if isinstance(value, bool):
        raise ThemeValidationError(path, "must be a number or length")
    if isinstance(value, (int, float)):
        amount = float(value)
        if amount < 0:
            raise ThemeValidationError(path, "must not be negative")
        return int(round(amount * _PT_TO_TWIPS))
    if isinstance(value, str):
        match = _LENGTH_RE.match(value)
        if not match:
            raise ThemeValidationError(path, "must be a number or length such as 6pt or 2cm")
        amount = float(match.group(1))
        unit = (match.group(2) or "pt").lower()
        if amount < 0:
            raise ThemeValidationError(path, "must not be negative")
        if unit in ("pt", "pts"):
            return int(round(amount * _PT_TO_TWIPS))
        if unit == "in":
            return int(round(amount * 1440))
        if unit == "cm":
            return int(round(amount * 567))
        if unit == "mm":
            return int(round(amount * 56.7))
        if unit in ("twip", "twips"):
            return int(round(amount))
        raise ThemeValidationError(path, f"unsupported unit {unit!r}")
    raise ThemeValidationError(path, "must be a number or length")
