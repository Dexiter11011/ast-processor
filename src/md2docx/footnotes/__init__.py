"""Footnote package module."""

from md2docx.footnotes.errors import DuplicateFootnoteError, FootnoteError, MissingFootnoteError
from md2docx.footnotes.manager import FootnoteManager

__all__ = [
    "DuplicateFootnoteError",
    "FootnoteError",
    "FootnoteManager",
    "MissingFootnoteError",
]
