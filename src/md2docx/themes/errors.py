"""Theme loading and validation errors."""

from __future__ import annotations


class ThemeError(Exception):
    """Base class for theme-related errors."""


class ThemeLoadError(ThemeError):
    """Failed to read or parse a theme file."""


class ThemeValidationError(ThemeError):
    """Theme data failed schema validation."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message
        if path:
            super().__init__(f"{path} {message}")
        else:
            super().__init__(message)
