"""Table formatting tests."""

from md2docx.ast.types import Document, Paragraph, Table, TableCell, TableRow, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_table_header_is_bold_and_centered():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Table(
                rows=[
                    TableRow(
                        header=True,
                        cells=[
                            TableCell(children=[Paragraph(children=[Text(value="Name")])]),
                            TableCell(children=[Paragraph(children=[Text(value="Age")])]),
                        ],
                    ),
                    TableRow(
                        cells=[
                            TableCell(children=[Paragraph(children=[Text(value="Bob")])]),
                            TableCell(children=[Paragraph(children=[Text(value="20")])]),
                        ],
                    ),
                ],
                column_aligns=["", ""],
            )
        ]
    )
    processor.process_document(doc, ctx)
    tbl = ctx.document.body_children[0]
    first_cell_p = tbl.findall(f".//{{{W_NS}}}tc")[0].find(f"{{{W_NS}}}p")
    jc = first_cell_p.find(f".//{{{W_NS}}}jc")
    assert jc is not None
    assert jc.get(f"{{{W_NS}}}val") == "center"
    assert first_cell_p.find(f".//{{{W_NS}}}b") is not None


def test_table_borders_none():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Table(
                borders="none",
                rows=[
                    TableRow(cells=[TableCell(children=[Paragraph(children=[Text(value="A")])])]),
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    tbl = ctx.document.body_children[0]
    borders = tbl.find(f".//{{{W_NS}}}tblBorders")
    assert borders is not None
    assert borders.find(f"{{{W_NS}}}top").get(f"{{{W_NS}}}val") == "nil"
