"""Metadata validation errors."""

from __future__ import annotations


class MetadataValidationError(ValueError):
    """Raised when metadata input fails validation."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)
