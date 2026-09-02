"""Template loading and merge errors."""

from __future__ import annotations


class TemplateError(Exception):
    """Base class for template-related errors."""


class TemplateLoadError(TemplateError):
    """Failed to read or parse a template DOCX."""


class TemplateInsertionError(TemplateError):
    """Template content insertion point is invalid."""


class TemplateMergeError(TemplateError):
    """Failed to merge generated content into a template."""


class TemplatePlaceholderError(TemplateError):
    """Template placeholder syntax, validation, or replacement failed."""
