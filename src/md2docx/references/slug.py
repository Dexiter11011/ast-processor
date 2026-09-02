"""Deterministic heading slug generation for bookmark names."""

from __future__ import annotations

import re
import unicodedata

_SLUG_SEPARATOR = re.compile(r"[\s\-_]+")
_NON_SLUG = re.compile(r"[^\w\-]+", re.UNICODE)
_COLLAPSE_HYPHENS = re.compile(r"-{2,}")
_EMPTY_SLUG_FALLBACK = "section"


def heading_plain_text(children) -> str:
    """Extract plain text from heading inline nodes (ignores formatting)."""
    parts: list[str] = []
    for child in children:
        if child.type == "text":
            parts.append(child.value)
        elif hasattr(child, "children"):
            parts.extend(_inline_plain_text(child.children))
    return "".join(parts)


def _inline_plain_text(children) -> list[str]:
    parts: list[str] = []
    for child in children:
        if child.type == "text":
            parts.append(child.value)
        elif hasattr(child, "children"):
            parts.extend(_inline_plain_text(child.children))
    return parts


def slugify(text: str) -> str:
    """Convert heading text to a deterministic bookmark slug."""
    normalized = unicodedata.normalize("NFKD", text.strip().casefold())
    normalized = _SLUG_SEPARATOR.sub("-", normalized)
    normalized = _NON_SLUG.sub("", normalized)
    normalized = _COLLAPSE_HYPHENS.sub("-", normalized).strip("-")
    return normalized or _EMPTY_SLUG_FALLBACK


def disambiguate_slug(base: str, used: dict[str, int]) -> str:
    """Return unique slug; first use keeps base, then base-1, base-2, …"""
    if base not in used:
        used[base] = 0
        return base
    used[base] += 1
    return f"{base}-{used[base]}"
