"""Resolve layout directive strings to PageLayout objects."""

from __future__ import annotations

from md2docx.sections.definition import PageLayout, PageMargins


def layout_from_spec(spec: str) -> PageLayout:
    normalized = spec.strip().lower().replace("_", "-")
    margins: PageMargins | None = None
    if "margins=" in normalized:
        base, _, margin_spec = normalized.partition("margins=")
        normalized = base.strip().rstrip("-")
        parts = [int(p.strip()) for p in margin_spec.split(",")]
        if len(parts) == 4:
            margins = PageMargins(parts[0], parts[1], parts[2], parts[3])

    if normalized in ("a4", "a4-portrait", "portrait"):
        return PageLayout.a4_portrait(margins=margins)
    if normalized in ("letter", "letter-portrait"):
        return PageLayout.letter_portrait(margins=margins)
    if normalized in ("landscape", "a4-landscape"):
        return PageLayout.a4_landscape(margins=margins)
    if normalized == "letter-landscape":
        return PageLayout.letter_landscape(margins=margins)
    return PageLayout.a4_portrait(margins=margins)
