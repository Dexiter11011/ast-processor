"""ListItemHandler unit tests."""

from md2docx.ast.types import Document, List, ListItem, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_list_item_processes_block_children():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=False,
                items=[
                    ListItem(
                        children=[
                            Paragraph(children=[Text(value="Alpha")]),
                            Paragraph(children=[Text(value="Beta")]),
                        ]
                    )
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    texts = [p.find(f".//{{{W_NS}}}t").text for p in ctx.document.body_children]
    assert texts == ["Alpha", "Beta"]
