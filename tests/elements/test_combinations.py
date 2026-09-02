"""Nested inline combination element tests."""

from md2docx.ast.types import Document, Emphasis, Paragraph, Strong, Text
from md2docx.elements import create_default_registry
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def _run_flags(run) -> tuple[bool, bool]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    return bold, italic


def test_nested_strong_emphasis_runs():
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(
        children=[
            Paragraph(
                children=[
                    Text(value="This is "),
                    Strong(
                        children=[
                            Text(value="bold and "),
                            Emphasis(children=[Text(value="italic")]),
                        ]
                    ),
                    Text(value="."),
                ]
            )
        ]
    )
    processor.process_document(doc, ctx)
    p = ctx.document.body_children[0]
    runs = p.findall(f"{{{W_NS}}}r")
    assert len(runs) == 4
    assert _run_flags(runs[2]) == (True, True)
