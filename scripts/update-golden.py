#!/usr/bin/env python3
"""Regenerate tests/expected/*.document.xml golden files from fixture markdown."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
EXPECTED = ROOT / "tests" / "expected"

GOLDEN_CASES = (
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
    "external-links",
    "internal-links",
    "bookmarks",
    "duplicate-heading-bookmarks",
    "toc",
    "toc-levels",
    "links-and-toc",
    "references-integration",
)


def _pretty_xml(data: bytes) -> str:
    root = etree.fromstring(data)
    return etree.tostring(root, pretty_print=True, encoding="unicode")


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from md2docx.pipeline import convert_markdown_to_docx

    EXPECTED.mkdir(parents=True, exist_ok=True)
    tmp_dir = ROOT / "out" / "_golden_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    updated = 0
    for case in GOLDEN_CASES:
        fixture = FIXTURES / f"{case}.md"
        if not fixture.is_file():
            print(f"skip {case}: missing {fixture.relative_to(ROOT)}", file=sys.stderr)
            continue
        docx_path = tmp_dir / f"{case}.docx"
        convert_markdown_to_docx(fixture, docx_path)
        with zipfile.ZipFile(docx_path, "r") as zf:
            document_xml = zf.read("word/document.xml")
        target = EXPECTED / f"{case}.document.xml"
        target.write_text(_pretty_xml(document_xml), encoding="utf-8")
        updated += 1
        print(f"updated {target.relative_to(ROOT)}")

    print(f"\n{updated} golden file(s) written to {EXPECTED.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
