"""Build programmatic AST fixtures for navigation (TOC, LOF, LOT, refs)."""

from __future__ import annotations

from md2docx.ast.types import Document, Heading, Image, ListOfFigures, ListOfTables, Paragraph, TableOfContents, Text
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption, CrossReferenceBlock, Figure, TableWithCaption
from md2docx.references.reference import CrossReference
from tests.figures_fixtures import _simple_table


def build_toc_levels_document() -> Document:
    return Document(
        children=[
            TableOfContents(min_level=2, max_level=3),
            Heading(level=1, children=[Text(value="Title")]),
            Heading(level=2, children=[Text(value="Section A")]),
            Heading(level=3, children=[Text(value="Subsection")]),
            Heading(level=4, children=[Text(value="Deep")]),
        ]
    )


def build_list_of_figures_document() -> Document:
    return Document(
        children=[
            ListOfFigures(),
            Figure(
                image=Image(src="logo.png", alt=""),
                caption=Caption(kind=CaptionKind.FIGURE, text="Architecture"),
            ),
            Figure(
                image=Image(src="one.png", alt=""),
                caption=Caption(kind=CaptionKind.FIGURE, text="Deployment"),
            ),
        ]
    )


def build_list_of_tables_document() -> Document:
    return Document(
        children=[
            ListOfTables(),
            TableWithCaption(
                table=_simple_table(("A", "B"), ("1", "2")),
                caption=Caption(kind=CaptionKind.TABLE, text="Results"),
            ),
            TableWithCaption(
                table=_simple_table(("X", "Y"), ("3", "4")),
                caption=Caption(kind=CaptionKind.TABLE, text="Metrics"),
            ),
        ]
    )


def build_mixed_navigation_document() -> Document:
    return Document(
        children=[
            TableOfContents(min_level=1, max_level=2),
            ListOfFigures(),
            ListOfTables(),
            Heading(level=1, children=[Text(value="Introduction")]),
            Heading(level=2, children=[Text(value="Architecture")]),
            Figure(
                image=Image(src="logo.png", alt=""),
                caption=Caption(kind=CaptionKind.FIGURE, text="Overview"),
            ),
            CrossReferenceBlock(
                reference=CrossReference(
                    target="figure-overview",
                    kind=CaptionKind.FIGURE,
                    prefix="See ",
                )
            ),
            TableWithCaption(
                table=_simple_table(("Name", "Value"), ("Latency", "12ms")),
                caption=Caption(kind=CaptionKind.TABLE, text="Benchmarks"),
            ),
            CrossReferenceBlock(
                reference=CrossReference(
                    target="table-benchmarks",
                    kind=CaptionKind.TABLE,
                    prefix="See ",
                )
            ),
        ]
    )


def build_bookmark_collision_document() -> Document:
    """Generated content with bookmark names that may collide with template."""
    return Document(
        children=[
            Heading(level=1, children=[Text(value="Architecture")]),
            Figure(
                image=Image(src="logo.png", alt=""),
                caption=Caption(kind=CaptionKind.FIGURE, text="Architecture"),
            ),
            TableWithCaption(
                table=_simple_table(("K", "V"), ("A", "1")),
                caption=Caption(kind=CaptionKind.TABLE, text="Results"),
            ),
            CrossReferenceBlock(
                reference=CrossReference(target="architecture", prefix="See ", kind=None)
            ),
            CrossReferenceBlock(
                reference=CrossReference(
                    target="figure-architecture",
                    kind=CaptionKind.FIGURE,
                    prefix="Figure ",
                )
            ),
            CrossReferenceBlock(
                reference=CrossReference(
                    target="table-results",
                    kind=CaptionKind.TABLE,
                    prefix="Table ",
                )
            ),
            Paragraph(children=[Text(value="End.")]),
        ]
    )
