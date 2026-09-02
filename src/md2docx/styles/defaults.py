"""Default style definitions — thin wrappers over ThemeResolver for compatibility."""

from __future__ import annotations

from md2docx.styles.definition import DocumentDefaults
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.resolver import ThemeResolver
from md2docx.styles.theme import DefaultTheme


def default_document_defaults() -> DocumentDefaults:
    return DefaultTheme.create().document_defaults


def build_default_definitions():
    """Return all default style definitions matching the pre-iteration-9 stylesheet."""
    return ThemeResolver.build_definitions(DefaultTheme.create().tokens)


def build_default_registry() -> StyleRegistry:
    return DefaultTheme.create().build_registry()
