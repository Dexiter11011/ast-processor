"""Public semantic API errors."""

from __future__ import annotations


class SemanticError(Exception):
    """Base class for semantic API errors."""

    code: str | None = None

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class InvalidStyleError(SemanticError):
    code = "invalid_style"


class InvalidBookmarkError(SemanticError):
    code = "invalid_bookmark"


class InvalidFieldError(SemanticError):
    code = "invalid_field"


class InvalidMediaError(SemanticError):
    code = "invalid_media"


class InvalidHyperlinkError(SemanticError):
    code = "invalid_hyperlink"


class EmptyParagraphError(SemanticError):
    code = "empty_paragraph"


class InvalidReferenceError(SemanticError):
    code = "invalid_reference"
