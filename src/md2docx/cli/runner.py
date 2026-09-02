"""CLI execution with unified error boundary."""

from __future__ import annotations

import sys
import traceback
from argparse import Namespace
from pathlib import Path

from md2docx.cli.diagnostics import Diagnostic, format_diagnostic
from md2docx.cli.errors import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    EXIT_USAGE,
    CliContext,
    Md2DocxError,
    diagnostic_from_exception,
    exit_code_for_exception,
    is_known_domain_error,
)
from md2docx.output.atomic import AtomicOutputError
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.plugins.loader import load_plugins
from md2docx.templates.errors import TemplateLoadError
from md2docx.templates.reader import DocxPackageReader
from md2docx.themes.errors import ThemeLoadError, ThemeValidationError
from md2docx.themes.loader import ThemeLoader


def _error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def _error_diagnostic(diagnostic: Diagnostic) -> None:
    _error(format_diagnostic(diagnostic))


def _validate_io_paths(input_path: Path, output_path: Path) -> Diagnostic | None:
    if not input_path.exists():
        return Diagnostic(message=f"input file does not exist: {input_path}")
    if not input_path.is_file():
        if input_path.is_dir():
            return Diagnostic(message=f"input path is not a file: {input_path}")
        return Diagnostic(message=f"input file does not exist: {input_path}")
    if output_path.exists() and output_path.is_dir():
        return Diagnostic(message=f"output path is a directory: {output_path}")
    try:
        if input_path.resolve() == output_path.resolve():
            return Diagnostic(message="input and output paths must differ")
    except OSError:
        pass
    return None


def run(args: Namespace) -> int:
    """Execute conversion with a single exception boundary."""
    debug = bool(getattr(args, "debug", False))
    input_path: Path = args.input
    output_path: Path = args.output if args.output else input_path.with_suffix(".docx")

    io_error = _validate_io_paths(input_path, output_path)
    if io_error is not None:
        _error_diagnostic(io_error)
        return EXIT_USAGE

    context = CliContext(input_path=input_path, output_path=output_path)

    theme = None
    if args.theme is not None:
        context = CliContext(
            input_path=input_path,
            output_path=output_path,
            theme_path=args.theme,
            template_path=args.template,
        )
        try:
            theme = ThemeLoader.load(args.theme)
        except (ThemeLoadError, ThemeValidationError) as exc:
            _error_diagnostic(diagnostic_from_exception(exc, context))
            return EXIT_FAILURE

    template = None
    if args.template is not None:
        context = CliContext(
            input_path=input_path,
            output_path=output_path,
            theme_path=args.theme,
            template_path=args.template,
        )
        try:
            template = DocxPackageReader.load(args.template)
        except TemplateLoadError as exc:
            _error_diagnostic(diagnostic_from_exception(exc, context))
            return EXIT_FAILURE

    plugin_registry = None
    if args.plugin:
        try:
            plugin_registry = load_plugins(list(args.plugin))
        except Exception as exc:
            _error_diagnostic(diagnostic_from_exception(exc, context))
            return EXIT_FAILURE

    update_fields: bool | None = None
    if args.update_fields:
        update_fields = True
    elif args.no_update_fields:
        update_fields = False

    try:
        convert_markdown_to_docx(
            input_path,
            output_path,
            theme=theme,
            template=template,
            plugin_registry=plugin_registry,
            cli_title=args.title,
            cli_author=args.author,
            cli_date=args.date,
            cli_subject=args.subject,
            cli_keywords=args.keywords,
            update_fields=update_fields,
            validate_before_commit=bool(args.validate),
        )
    except AtomicOutputError as exc:
        _error(str(exc))
        return EXIT_FAILURE
    except Exception as exc:
        if is_known_domain_error(exc):
            _error_diagnostic(diagnostic_from_exception(exc, context))
            return exit_code_for_exception(exc)
        if debug:
            traceback.print_exc()
        else:
            _error(f"internal error: {exc}")
        return EXIT_FAILURE

    return EXIT_SUCCESS
