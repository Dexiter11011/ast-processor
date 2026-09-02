"""AstProcessor tests."""

from md2docx.ast.types import Document, HorizontalRule, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def test_empty_document_does_not_raise():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    processor.process_document(Document(children=[]), ctx)
    assert ctx.document.body_children == []


def test_paragraph_with_text_produces_body_element():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Paragraph(children=[Text(value="Hello")])])
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 1
    assert ctx.document.body_children[0].tag == f"{{{W_NS}}}p"


def test_heading_with_text_produces_styled_paragraph():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    from md2docx.ast.types import Heading

    doc = Document(children=[Heading(level=1, children=[Text(value="Title")])])
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 1
    p_style = ctx.document.body_children[0].find(f".//{{{W_NS}}}pStyle")
    assert p_style is not None
    assert p_style.get(f"{{{W_NS}}}val") == "Heading1"


def test_horizontal_rule_produces_body_element():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[HorizontalRule()])
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 1
    p_pr = ctx.document.body_children[0].find(f"{{{W_NS}}}pPr")
    assert p_pr is not None
    assert p_pr.find(f"{{{W_NS}}}pBdr") is not None


def test_process_children_only_walks_children_field():
    from md2docx.ast.types import List, ListItem, Table, TableRow

    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=True,
                items=[ListItem(children=[Paragraph(children=[Text(value="One")])])],
            ),
            Table(rows=[TableRow(cells=[])]),
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 3
    assert ctx.document.body_children[0].tag == f"{{{W_NS}}}p"
    assert ctx.document.body_children[1].tag == f"{{{W_NS}}}tbl"
    assert ctx.document.body_children[2].tag == f"{{{W_NS}}}p"
