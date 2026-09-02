"""Build programmatic AST fixtures for figures, tables, and cross-references."""

from __future__ import annotations

from md2docx.ast.types import Document, Image, Paragraph, Table, TableCell, TableRow, Text
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption, CrossReferenceBlock, Figure, TableWithCaption
from md2docx.references.reference import CrossReference


def _simple_table(*rows: tuple[str, ...]) -> Table:
    table_rows: list[TableRow] = []
    for index, row in enumerate(rows):
        cells = [
            TableCell(children=[Paragraph(children=[Text(value=cell)])])
            for cell in row
        ]
        table_rows.append(TableRow(cells=cells, header=index == 0))
    return Table(rows=table_rows)


def build_interleaved_figures_tables_document() -> Document:
    """Figure, Table, Figure, Table, Figure with cross-references."""
    figure_a = Figure(
        image=Image(src="logo.png", alt=""),
        caption=Caption(kind=CaptionKind.FIGURE, text="Architecture overview"),
    )
    table_a = TableWithCaption(
        table=_simple_table(("Name", "Value"), ("A", "1")),
        caption=Caption(kind=CaptionKind.TABLE, text="Configuration values"),
    )
    figure_b = Figure(
        image=Image(src="one.png", alt=""),
        caption=Caption(kind=CaptionKind.FIGURE, text="Component diagram"),
    )
    table_b = TableWithCaption(
        table=_simple_table(("Metric", "Score"), ("Latency", "12")),
        caption=Caption(kind=CaptionKind.TABLE, text="Benchmark results"),
    )
    figure_c = Figure(
        image=Image(src="two.png", alt=""),
        caption=Caption(kind=CaptionKind.FIGURE, text="Deployment topology"),
    )
    return Document(
        children=[
            Paragraph(children=[Text(value="Introduction.")]),
            figure_a,
            CrossReferenceBlock(
                reference=CrossReference(
                    target="figure-architecture-overview",
                    kind=CaptionKind.FIGURE,
                    prefix="Described in ",
                )
            ),
            table_a,
            CrossReferenceBlock(
                reference=CrossReference(
                    target="table-configuration-values",
                    kind=CaptionKind.TABLE,
                    prefix="See ",
                )
            ),
            figure_b,
            table_b,
            figure_c,
            CrossReferenceBlock(
                reference=CrossReference(
                    target="figure-deployment-topology",
                    kind=CaptionKind.FIGURE,
                    prefix="Final layout in ",
                )
            ),
        ]
    )


def build_single_figure_document() -> Document:
    return Document(
        children=[
            Figure(
                image=Image(src="logo.png", alt=""),
                caption=Caption(kind=CaptionKind.FIGURE, text="Architecture"),
            )
        ]
    )


def build_single_table_document() -> Document:
    return Document(
        children=[
            TableWithCaption(
                table=_simple_table(("Col", "Data"), ("X", "Y")),
                caption=Caption(kind=CaptionKind.TABLE, text="Results"),
            )
        ]
    )
