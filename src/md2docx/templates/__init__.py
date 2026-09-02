"""External DOCX template loading and merging."""

from md2docx.templates.errors import (
    TemplateError,
    TemplateInsertionError,
    TemplateLoadError,
    TemplateMergeError,
    TemplatePlaceholderError,
)
from md2docx.processor.errors import TemplateModeError
from md2docx.templates.merger import TemplateMerger
from md2docx.templates.package import TemplatePackage
from md2docx.templates.reader import DocxPackageReader

__all__ = [
    "DocxPackageReader",
    "TemplateError",
    "TemplateInsertionError",
    "TemplateLoadError",
    "TemplateMergeError",
    "TemplatePlaceholderError",
    "TemplateMerger",
    "TemplateModeError",
    "TemplatePackage",
]
