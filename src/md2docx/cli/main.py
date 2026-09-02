"""md2docx CLI entry point."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from md2docx.cli.runner import run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2docx",
        description="Convert Markdown to DOCX.",
        epilog=(
            "Examples:\n"
            "  md2docx input.md\n"
            "  md2docx input.md -o output.docx\n"
            "  md2docx input.md --theme corporate.yaml -o output.docx\n"
            "  md2docx input.md --template corporate.docx -o output.docx\n"
            "  md2docx input.md --template placeholders.docx \\\n"
            "    --title \"Project Documentation\" --author \"John Doe\" --date 2026-08-31 \\\n"
            "    -o output.docx\n"
            "  md2docx input.md --plugin examples/plugins/notes_plugin.py -o output.docx\n"
            "  md2docx input.md -o output.docx --validate"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="input Markdown file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="OUTPUT",
        help="output DOCX file (default: input name with .docx extension)",
    )
    parser.add_argument(
        "--theme",
        type=Path,
        default=None,
        metavar="PATH",
        help="Use external YAML document theme.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        metavar="PATH",
        help="Use an existing DOCX document as a template.",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        metavar="TEXT",
        help="Document title for template placeholders and core properties.",
    )
    parser.add_argument(
        "--author",
        type=str,
        default=None,
        metavar="TEXT",
        help="Document author for template placeholders and core properties.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        metavar="TEXT",
        help="Document date for template placeholders (explicit value only).",
    )
    parser.add_argument(
        "--subject",
        type=str,
        default=None,
        metavar="TEXT",
        help="Document subject for template placeholders and core properties.",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default=None,
        metavar="TEXT",
        help="Document keywords (comma-separated) for placeholders and core properties.",
    )
    update_fields_group = parser.add_mutually_exclusive_group()
    update_fields_group.add_argument(
        "--update-fields",
        action="store_true",
        help="Update dynamic Word fields when the document opens.",
    )
    update_fields_group.add_argument(
        "--no-update-fields",
        action="store_true",
        help="Do not set update fields on open in word/settings.xml.",
    )
    parser.add_argument(
        "--plugin",
        type=Path,
        action="append",
        default=None,
        metavar="PATH",
        help="Load a Python plugin from PATH (repeatable).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="validate the generated DOCX package after conversion",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print full traceback for unexpected internal errors",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('md2docx')}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
