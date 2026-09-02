"""Deterministic bookmark naming for captioned objects."""

from __future__ import annotations

from md2docx.captions.kinds import CaptionKind
from md2docx.references.slug import disambiguate_slug, slugify

_PREFIX = {
    CaptionKind.FIGURE: "figure",
    CaptionKind.TABLE: "table",
}


def caption_bookmark_name(
    kind: CaptionKind,
    caption_text: str,
    used: dict[str, int],
) -> str:
    """Return a stable bookmark name such as figure-architecture or table-results."""
    prefix = _PREFIX[kind]
    slug = slugify(caption_text) if caption_text.strip() else "caption"
    base = f"{prefix}-{slug}"
    return disambiguate_slug(base, used)
