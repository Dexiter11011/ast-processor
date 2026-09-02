"""Helpers for navigation Markdown DSL tests."""

from __future__ import annotations

from md2docx.ast.types import Document
from md2docx.parser.caption_transform import apply_caption_transform
from md2docx.parser.markdown_parser import MarkdownParser


def parse_navigation_markdown(source: str, *, source_path: str | None = None) -> Document:
    document = MarkdownParser().parse(source)
    return apply_caption_transform(document, source_path=source_path)
