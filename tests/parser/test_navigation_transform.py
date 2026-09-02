"""Tests for navigation AST deduplication against template regions."""

from __future__ import annotations

from md2docx.ast.types import Document, Heading, ListOfFigures, ListOfTables, Paragraph, TableOfContents, Text
from md2docx.parser.navigation_transform import strip_navigation_for_template_regions


def test_strip_removes_toc_when_template_provides_toc_region():
    document = Document(
        children=[
            TableOfContents(min_level=1, max_level=3),
            Heading(level=1, children=[Text(value="Title")]),
        ]
    )
    result = strip_navigation_for_template_regions(document, {"toc"})
    assert len(result.children) == 1
    assert result.children[0].type == "heading"


def test_strip_removes_all_navigation_kinds():
    document = Document(
        children=[
            TableOfContents(min_level=1, max_level=3),
            ListOfFigures(),
            ListOfTables(),
            Paragraph(children=[Text(value="Body")]),
        ]
    )
    result = strip_navigation_for_template_regions(
        document,
        {"toc", "list_of_figures", "list_of_tables"},
    )
    assert len(result.children) == 1
    assert result.children[0].type == "paragraph"


def test_strip_leaves_ast_unchanged_without_matching_regions():
    document = Document(children=[TableOfContents(min_level=1, max_level=3)])
    result = strip_navigation_for_template_regions(document, set())
    assert result is document
