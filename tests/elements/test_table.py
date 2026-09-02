"""Table element tests."""

from md2docx.ast.types import Document, Paragraph, Table, TableCell, TableRow, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_table_handler_builds_tbl():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Table(
                rows=[
                    TableRow(
                        cells=[
                            TableCell(children=[Paragraph(children=[Text(value="Name")])]),
                            TableCell(children=[Paragraph(children=[Text(value="Age")])]),
                        ]
                    ),
                    TableRow(
                        cells=[
                            TableCell(children=[Paragraph(children=[Text(value="Bob")])]),
                            TableCell(children=[Paragraph(children=[Text(value="20")])]),
                        ]
                    ),
                ]
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    tbl = ctx.document.body_children[0]
    assert tbl.tag == f"{{{W_NS}}}tbl"
    assert ctx.document.body_children[1].tag == f"{{{W_NS}}}p"
    texts = [t.text for t in tbl.findall(f".//{{{W_NS}}}t")]
    assert texts == ["Name", "Age", "Bob", "20"]
