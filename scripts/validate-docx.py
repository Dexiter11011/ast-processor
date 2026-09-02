#!/usr/bin/env python3
"""Validate DOCX package structure and references.

Pipeline:
  Markdown → DOCX (optional) → unzip → validate package → XML → relationships → references
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXTURES = (
    "empty",
    "hello-world",
    "multiple-paragraphs",
    "headings",
    "bold",
    "italic",
    "combinations",
    "inline-code",
    "link",
    "unordered-list",
    "ordered-list",
    "nested-list",
    "blockquote",
    "horizontal-rule",
    "code-block",
    "xml-escaping",
    "image",
    "table",
    "table-variants",
    "advanced-tables",
    "nested-inline",
    "escaping-edge-cases",
    "document-metadata",
    "page-break",
    "landscape",
    "header-footer",
    "sections-integration",
    "integration-article",
    "all-iterations",
    "external-links",
    "internal-links",
    "bookmarks",
    "duplicate-heading-bookmarks",
    "toc",
    "toc-levels",
    "links-and-toc",
    "references-integration",
    "gfm-integration",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate-docx",
        description="Validate OOXML DOCX package integrity, XML, relationships, and references.",
    )
    parser.add_argument(
        "docx",
        nargs="*",
        type=Path,
        help="DOCX file(s) to validate",
    )
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="convert all test fixtures to DOCX and validate each one",
    )
    parser.add_argument(
        "--warnings",
        action="store_true",
        help="print warnings in addition to errors",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from md2docx.pipeline import convert_markdown_to_docx
    from md2docx.validation import validate_docx

    parser = _build_parser()
    args = parser.parse_args(argv)

    targets: list[Path] = list(args.docx)
    if args.fixtures:
        fixtures_dir = ROOT / "tests" / "fixtures"
        tmp_dir = ROOT / "out" / "_validate_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        for name in FIXTURES:
            md_path = fixtures_dir / f"{name}.md"
            if not md_path.is_file():
                print(f"skip missing fixture: {md_path}", file=sys.stderr)
                continue
            docx_path = tmp_dir / f"{name}.docx"
            convert_markdown_to_docx(md_path, docx_path)
            targets.append(docx_path)

    if not targets:
        parser.error("provide DOCX path(s) or use --fixtures")

    failed = 0
    for path in targets:
        report = validate_docx(path)
        errors = [i for i in report.issues if i.severity == "error"]
        warnings = [i for i in report.issues if i.severity == "warning"]
        if errors:
            failed += 1
            print(f"FAIL {path}", file=sys.stderr)
            for issue in errors:
                prefix = f"  [{issue.category}]"
                if issue.part:
                    prefix += f" {issue.part}:"
                print(f"{prefix} {issue.message}", file=sys.stderr)
        else:
            print(f"OK   {path}")
        if args.warnings and warnings:
            for issue in warnings:
                prefix = f"  [{issue.category}]"
                if issue.part:
                    prefix += f" {issue.part}:"
                print(f"{prefix} {issue.message}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
