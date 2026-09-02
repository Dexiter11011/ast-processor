"""CLI error mapping and exit code policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from md2docx.cli.diagnostics import Diagnostic, format_diagnostic
from md2docx.fields.errors import FieldError, MissingRefTargetError
from md2docx.footnotes.errors import FootnoteError
from md2docx.metadata.errors import MetadataValidationError
from md2docx.navigation.errors import NavigationError, ReferenceKindMismatchError
from md2docx.parser.errors import CaptionParseError, FootnoteParseError, HtmlParseError
from md2docx.plugin_api.errors import PluginError
from md2docx.processor.errors import ImageNotFoundError, ImagePathError, TemplateModeError, UnsupportedNodeError
from md2docx.semantic.errors import SemanticError
from md2docx.templates.errors import (
    TemplateError,
    TemplateInsertionError,
    TemplateMergeError,
    TemplatePlaceholderError,
)
from md2docx.themes.errors import ThemeError, ThemeLoadError, ThemeValidationError


EXIT_SUCCESS = 0
EXIT_USAGE = 1
EXIT_FAILURE = 2


class Md2DocxError(Exception):
    """Marker for errors with an attached CLI diagnostic."""

    def __init__(self, diagnostic: Diagnostic, *, exit_code: int = EXIT_FAILURE) -> None:
        super().__init__(format_diagnostic(diagnostic))
        self.diagnostic = diagnostic
        self.exit_code = exit_code


@dataclass(frozen=True)
class CliContext:
    input_path: Path | None = None
    output_path: Path | None = None
    theme_path: Path | None = None
    template_path: Path | None = None


def diagnostic_from_exception(exc: BaseException, context: CliContext | None = None) -> Diagnostic:
    """Map a domain exception to a CLI diagnostic."""
    ctx = context or CliContext()
    code = getattr(exc, "code", None)

    if isinstance(exc, ThemeLoadError):
        return Diagnostic(code=code or "theme_load_error", message=str(exc))
    if isinstance(exc, ThemeValidationError):
        if exc.path:
            message = f"invalid theme: {exc.path} {exc.message}"
        else:
            message = f"invalid theme: {exc.message}"
        return Diagnostic(code=code or "invalid_theme", message=message)
    if isinstance(exc, ThemeError):
        return Diagnostic(code=code or "theme_error", message=str(exc), path=str(ctx.theme_path) if ctx.theme_path else None)
    if isinstance(exc, TemplateError):
        return Diagnostic(
            code=code or "template_error",
            message=str(exc),
            path=str(ctx.template_path) if ctx.template_path else None,
        )
    if isinstance(exc, MetadataValidationError):
        message = str(exc)
        if exc.field:
            message = f'invalid metadata field "{exc.field}": {exc}'
        return Diagnostic(code=code or "invalid_metadata", message=message, path=str(ctx.input_path) if ctx.input_path else None)
    if isinstance(exc, (CaptionParseError, FootnoteParseError, HtmlParseError)):
        path = exc.path or (str(ctx.input_path) if ctx.input_path else None)
        return Diagnostic(code=code or "markdown_parse_error", message=str(exc), path=path, line=exc.line)
    if isinstance(exc, PluginError):
        return Diagnostic(code=code or "plugin_error", message=str(exc))
    if isinstance(exc, SemanticError):
        return Diagnostic(code=code or "semantic_error", message=str(exc))
    if isinstance(exc, (NavigationError, FootnoteError)):
        return Diagnostic(code=code or exc.__class__.__name__.lower(), message=str(exc), path=str(ctx.input_path) if ctx.input_path else None)
    if isinstance(exc, (FieldError, MissingRefTargetError, ReferenceKindMismatchError)):
        return Diagnostic(code=code or "reference_error", message=str(exc), path=str(ctx.input_path) if ctx.input_path else None)
    if isinstance(exc, (UnsupportedNodeError, TemplateModeError, ImageNotFoundError, ImagePathError)):
        return Diagnostic(code=code or "processing_error", message=str(exc), path=str(ctx.input_path) if ctx.input_path else None)
    if isinstance(exc, TemplateInsertionError):
        return Diagnostic(code=code or "template_insertion_error", message=str(exc))
    if isinstance(exc, TemplatePlaceholderError):
        return Diagnostic(code=code or "template_placeholder_error", message=str(exc))
    if isinstance(exc, TemplateMergeError):
        return Diagnostic(code=code or "template_merge_error", message=str(exc))
    if isinstance(exc, OSError):
        return Diagnostic(code=code or "output_error", message=str(exc), path=str(ctx.output_path) if ctx.output_path else None)
    return Diagnostic(code=code or "internal_error", message=str(exc))


def exit_code_for_exception(exc: BaseException) -> int:
    if isinstance(exc, Md2DocxError):
        return exc.exit_code
    return EXIT_FAILURE


def is_known_domain_error(exc: BaseException) -> bool:
    known = (
        ThemeError,
        TemplateError,
        TemplateInsertionError,
        TemplatePlaceholderError,
        TemplateMergeError,
        MetadataValidationError,
        CaptionParseError,
        FootnoteParseError,
        HtmlParseError,
        PluginError,
        SemanticError,
        NavigationError,
        FootnoteError,
        FieldError,
        MissingRefTargetError,
        ReferenceKindMismatchError,
        UnsupportedNodeError,
        TemplateModeError,
        ImageNotFoundError,
        ImagePathError,
        OSError,
        Md2DocxError,
    )
    return isinstance(exc, known)
