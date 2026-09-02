"""ListHandler tests."""

from typing import Optional

from lxml import etree

from md2docx.ast.types import Document, List, ListItem, Paragraph, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def _paragraph_style(paragraph) -> Optional[str]:
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    if p_style is None:
        return None
    return p_style.get(f"{{{W_NS}}}val")


def test_list_produces_numbered_paragraphs():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=False,
                items=[
                    ListItem(children=[Paragraph(children=[Text(value="One")])]),
                    ListItem(children=[Paragraph(children=[Text(value="Two")])]),
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    for p in ctx.document.body_children:
        assert _paragraph_style(p) == "ListParagraph"


def test_ordered_list_uses_separate_style_after_separator():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(ordered=False, items=[ListItem(children=[Paragraph(children=[Text(value="A")])])]),
            List(
                ordered=True,
                items=[
                    ListItem(children=[Paragraph(children=[Text(value="First")])]),
                ],
            ),
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 3
    assert _paragraph_style(ctx.document.body_children[0]) == "ListParagraph"
    assert _paragraph_style(ctx.document.body_children[1]) == "Normal"
    assert _paragraph_style(ctx.document.body_children[2]) == "ListParagraph"


def _list_ilvl(paragraph) -> Optional[str]:
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return "0"
    num_pr = p_pr.find(f"{{{W_NS}}}numPr")
    if num_pr is None:
        return "0"
    ilvl = num_pr.find(f"{{{W_NS}}}ilvl")
    return ilvl.get(f"{{{W_NS}}}val") if ilvl is not None else "0"


def test_nested_list_sets_ilvl_on_child_items():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=False,
                items=[
                    ListItem(
                        children=[
                            Paragraph(children=[Text(value="One")]),
                            List(
                                ordered=False,
                                items=[
                                    ListItem(children=[Paragraph(children=[Text(value="Nested")])]),
                                ],
                            ),
                        ]
                    )
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    assert _list_ilvl(ctx.document.body_children[0]) == "0"
    assert _list_ilvl(ctx.document.body_children[1]) == "1"
    num_pr = ctx.document.body_children[1].find(f".//{{{W_NS}}}numPr")
    assert num_pr is not None
    assert num_pr.find(f"{{{W_NS}}}numId").get(f"{{{W_NS}}}val") == "3"


def _list_num_id(paragraph) -> Optional[str]:
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    num_pr = p_pr.find(f"{{{W_NS}}}numPr")
    if num_pr is None:
        return None
    num_id = num_pr.find(f"{{{W_NS}}}numId")
    return num_id.get(f"{{{W_NS}}}val") if num_id is not None else None


def test_nested_ordered_under_sibling_bullets_restart_numbering():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=False,
                items=[
                    ListItem(
                        children=[
                            Paragraph(children=[Text(value="Solar")]),
                            List(
                                ordered=True,
                                items=[
                                    ListItem(children=[Paragraph(children=[Text(value="A1")])]),
                                    ListItem(children=[Paragraph(children=[Text(value="A2")])]),
                                ],
                            ),
                        ]
                    ),
                    ListItem(
                        children=[
                            Paragraph(children=[Text(value="Wind")]),
                            List(
                                ordered=True,
                                items=[
                                    ListItem(children=[Paragraph(children=[Text(value="B1")])]),
                                    ListItem(children=[Paragraph(children=[Text(value="B2")])]),
                                ],
                            ),
                        ]
                    ),
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    ordered_items = [
        p
        for p in ctx.document.body_children
        if _list_ilvl(p) == "1" and _list_num_id(p) is not None
    ]
    assert len(ordered_items) == 4
    first_num_id = _list_num_id(ordered_items[0])
    second_num_id = _list_num_id(ordered_items[2])
    assert first_num_id != second_num_id
    numbering = etree.fromstring(ctx.numbering.to_bytes())
    num = next(
        n
        for n in numbering.findall(f"{{{W_NS}}}num")
        if n.get(f"{{{W_NS}}}numId") == second_num_id
    )
    override = num.find(f"{{{W_NS}}}lvlOverride")
    assert override is not None
    assert override.get(f"{{{W_NS}}}ilvl") == "1"
    start = override.find(f"{{{W_NS}}}startOverride")
    assert start is not None
    assert start.get(f"{{{W_NS}}}val") == "1"


def test_mixed_nested_list_allocates_new_num_id_for_kind_change():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            List(
                ordered=False,
                items=[
                    ListItem(
                        children=[
                            Paragraph(children=[Text(value="Bullet")]),
                            List(
                                ordered=True,
                                items=[
                                    ListItem(children=[Paragraph(children=[Text(value="Numbered")])]),
                                ],
                            ),
                        ]
                    )
                ],
            )
        ]
    )
    processor.process_document(doc, ctx)
    assert len(ctx.document.body_children) == 2
    parent_num = _list_num_id(ctx.document.body_children[0])
    nested_num = _list_num_id(ctx.document.body_children[1])
    assert parent_num is not None
    assert nested_num is not None
    assert parent_num != nested_num
