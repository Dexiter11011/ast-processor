"""Formatting leakage regression tests."""

from __future__ import annotations

from md2docx.ast.types import Document, Emphasis, Paragraph, Strong, Text
from md2docx.elements import create_default_registry
from md2docx.elements.inline_runs import collect_runs
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from tests.helpers import W_NS


def _run_flags(run) -> tuple[bool, bool]:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    bold = r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None
    italic = r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None
    return bold, italic


def _run_text(run) -> str:
    text_el = run.find(f"{{{W_NS}}}t")
    return text_el.text if text_el is not None else ""


def _process_paragraph(markdown_parts: list) -> list:
    ctx = ProcessingContext.create_default()
    processor = AstProcessor(create_default_registry())
    doc = Document(children=[Paragraph(children=markdown_parts)])
    processor.process_document(doc, ctx)
    paragraph = doc.children[0]
    return collect_runs(paragraph, ctx, processor)


def test_normal_bold_normal():
    runs = _process_paragraph(
        [Text(value="Normal "), Strong(children=[Text(value="bold")]), Text(value=" normal.")]
    )
    assert len(runs) == 3
    assert _run_flags(runs[0]) == (False, False)
    assert _run_flags(runs[1]) == (True, False)
    assert _run_flags(runs[2]) == (False, False)


def test_bold_then_normal():
    runs = _process_paragraph([Strong(children=[Text(value="bold")]), Text(value=" normal")])
    assert len(runs) == 2
    assert _run_flags(runs[0]) == (True, False)
    assert _run_flags(runs[1]) == (False, False)


def test_normal_then_bold():
    runs = _process_paragraph([Text(value="normal "), Strong(children=[Text(value="bold")])])
    assert len(runs) == 2
    assert _run_flags(runs[0]) == (False, False)
    assert _run_flags(runs[1]) == (True, False)


def test_alternating_bold_segments():
    runs = _process_paragraph(
        [
            Text(value="normal "),
            Strong(children=[Text(value="bold")]),
            Text(value=" normal "),
            Strong(children=[Text(value="bold")]),
        ]
    )
    assert len(runs) == 4
    assert _run_flags(runs[0]) == (False, False)
    assert _run_flags(runs[1]) == (True, False)
    assert _run_flags(runs[2]) == (False, False)
    assert _run_flags(runs[3]) == (True, False)


def test_emphasis_does_not_leak_after_strong():
    runs = _process_paragraph(
        [
            Strong(children=[Emphasis(children=[Text(value="both")])]),
            Text(value=" plain"),
        ]
    )
    assert _run_flags(runs[0]) == (True, True)
    assert _run_flags(runs[1]) == (False, False)
    assert _run_text(runs[1]) == " plain"
