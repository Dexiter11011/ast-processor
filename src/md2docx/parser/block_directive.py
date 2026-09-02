"""Parse block-level HTML comment directives."""

from __future__ import annotations

import re

from md2docx.captions.kinds import CaptionKind

PAGE_BREAK = re.compile(r"^\s*<!--\s*pagebreak\s*-->\s*$", re.IGNORECASE)
SECTION = re.compile(
    r"^\s*<!--\s*section:\s*(?P<spec>[^-]+(?:-[^-]+)*)\s*-->\s*$",
    re.IGNORECASE,
)
HEADER = re.compile(r"^\s*<!--\s*header:\s*(?P<text>.+?)\s*-->\s*$", re.IGNORECASE)
FOOTER = re.compile(r"^\s*<!--\s*footer:\s*(?P<text>.+?)\s*-->\s*$", re.IGNORECASE)
FIELD = re.compile(r"^\s*<!--\s*field:\s*(?P<spec>.+?)\s*-->\s*$", re.IGNORECASE)
TOC = re.compile(
    r"^\s*<!--\s*toc(?::\s*(?P<levels>\d+\s*-\s*\d+))?\s*-->\s*$",
    re.IGNORECASE,
)
LOF = re.compile(r"^\s*<!--\s*lof\s*-->\s*$", re.IGNORECASE)
LOT = re.compile(r"^\s*<!--\s*lot\s*-->\s*$", re.IGNORECASE)
CAPTION = re.compile(
    r"^\s*<!--\s*caption:\s*(?P<kind>figure|table)\s+(?P<text>.+?)\s*-->\s*$",
    re.IGNORECASE,
)
REF = re.compile(
    r'^\s*<!--\s*ref:\s*(?P<kind>figure|table)\s+(?P<slug>[A-Za-z0-9][\w\-]*)(?:\s+prefix="(?P<prefix>[^"]*)")?\s*-->\s*$',
    re.IGNORECASE,
)


def match_page_break(line: str) -> bool:
    return PAGE_BREAK.match(line) is not None


def match_section_break(line: str) -> str | None:
    match = SECTION.match(line)
    return match.group("spec").strip().lower() if match else None


def match_header_directive(line: str) -> str | None:
    match = HEADER.match(line)
    return match.group("text").strip() if match else None


def match_footer_directive(line: str) -> str | None:
    match = FOOTER.match(line)
    return match.group("text").strip() if match else None


def match_field_directive(line: str) -> tuple[str, str] | None:
    match = FIELD.match(line)
    if match is None:
        return None
    parts = match.group("spec").strip().split(None, 1)
    kind = parts[0].lower()
    target = parts[1].strip() if len(parts) > 1 else ""
    return kind, target


def match_toc_directive(line: str) -> tuple[int, int] | None:
    match = TOC.match(line)
    if match is None:
        return None
    levels = match.group("levels")
    if not levels:
        return (1, 3)
    parts = re.split(r"\s*-\s*", levels.strip())
    if len(parts) != 2:
        return (1, 3)
    return (int(parts[0]), int(parts[1]))


def match_lof_directive(line: str) -> bool:
    return LOF.match(line) is not None


def match_lot_directive(line: str) -> bool:
    return LOT.match(line) is not None


def match_caption_directive(line: str) -> tuple[CaptionKind, str] | None:
    match = CAPTION.match(line)
    if match is None:
        return None
    kind_text = match.group("kind").lower()
    kind = CaptionKind.FIGURE if kind_text == "figure" else CaptionKind.TABLE
    return kind, match.group("text").strip()


def match_ref_directive(line: str) -> tuple[CaptionKind, str, str] | None:
    match = REF.match(line)
    if match is None:
        return None
    kind_text = match.group("kind").lower()
    kind = CaptionKind.FIGURE if kind_text == "figure" else CaptionKind.TABLE
    slug = match.group("slug").strip()
    prefix = match.group("prefix")
    if prefix is None:
        prefix = "See "
    return kind, slug, prefix
