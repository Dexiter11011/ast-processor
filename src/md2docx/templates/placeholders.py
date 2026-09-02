"""Template placeholder model and known-name registry."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlaceholderKind(Enum):
    """Semantic kind of a template placeholder."""

    CONTENT = "content"
    NAVIGATION = "navigation"
    PLUGIN = "plugin"
    SCALAR = "scalar"


KNOWN_PLACEHOLDERS: dict[str, PlaceholderKind] = {
    "content": PlaceholderKind.CONTENT,
    "toc": PlaceholderKind.NAVIGATION,
    "list_of_figures": PlaceholderKind.NAVIGATION,
    "list_of_tables": PlaceholderKind.NAVIGATION,
    "title": PlaceholderKind.SCALAR,
    "author": PlaceholderKind.SCALAR,
    "date": PlaceholderKind.SCALAR,
    "subject": PlaceholderKind.SCALAR,
    "keywords": PlaceholderKind.SCALAR,
}


@dataclass(frozen=True)
class TemplatePlaceholder:
    """A detected placeholder in template document.xml."""

    name: str
    kind: PlaceholderKind
    paragraph_index: int
    raw: str


def kind_for_name(name: str, *, extra: dict[str, PlaceholderKind] | None = None) -> PlaceholderKind | None:
    """Return the kind for a normalized placeholder name, if known."""
    if extra and name in extra:
        return extra[name]
    return KNOWN_PLACEHOLDERS.get(name)
