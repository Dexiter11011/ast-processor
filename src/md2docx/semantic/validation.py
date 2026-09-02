"""Validation helpers for the public semantic API."""

from __future__ import annotations

import re

from md2docx.semantic.errors import (
    EmptyParagraphError,
    InvalidBookmarkError,
    InvalidHyperlinkError,
)

_BOOKMARK_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-_]*$")
_BLOCKED_URL_SCHEMES = ("javascript:", "data:", "vbscript:")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value)


def validate_paragraph_children(children: tuple) -> None:
    if not children:
        raise EmptyParagraphError("paragraph must contain at least one inline child")


def validate_bookmark_name(name: str) -> None:
    cleaned = name.strip()
    if not cleaned or not _BOOKMARK_PATTERN.match(cleaned):
        raise InvalidBookmarkError(f"invalid bookmark name: {name!r}")


def validate_external_url(url: str) -> None:
    lowered = url.strip().lower()
    if any(lowered.startswith(scheme) for scheme in _BLOCKED_URL_SCHEMES):
        raise InvalidHyperlinkError(f"unsupported hyperlink URL scheme: {url!r}")


def validate_internal_anchor(anchor: str) -> None:
    validate_bookmark_name(anchor.lstrip("#"))
