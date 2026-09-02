#!/usr/bin/env python3
"""Build example DOCX files demonstrating dynamic fields."""

from __future__ import annotations

from pathlib import Path

from md2docx.pipeline import convert_markdown_to_docx

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples" / "fields"
MARKDOWN = """---
title: Project Documentation
author: John Doe
---

<!-- header: title-field -->
<!-- footer: page-numbers -->

# Project Documentation

Introduction paragraph.
"""


def main() -> None:
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    markdown_path = EXAMPLES_DIR / "sample.md"
    markdown_path.write_text(MARKDOWN, encoding="utf-8")
    output = EXAMPLES_DIR / "sample.docx"
    convert_markdown_to_docx(
        markdown_path,
        output,
        cli_title="Project Documentation",
        cli_author="John Doe",
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
