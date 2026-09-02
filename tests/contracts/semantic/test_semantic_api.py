"""Contract tests for the public semantic API."""

from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag
from md2docx.semantic import (
    EmptyParagraphError,
    InvalidHyperlinkError,
    InvalidStyleError,
    RichDocumentFragment,
    SemanticContext,
    bold,
    bullet_list,
    figure,
    fragment,
    hyperlink,
    italic,
    line_break,
    list_item,
    paragraph,
    text,
    title_field,
)
from md2docx.semantic.renderer import SemanticRenderer
from tests.contracts.helpers.semantic_docx import assert_contains_paragraph


def _document_xml_from_context(context) -> bytes:
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    for child in context.document.body_children:
        body.append(child)
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    return serialize(root)


def test_empty_fragment_produces_no_output(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    sem = SemanticContext.from_processing_context(context)
    SemanticRenderer.render_to_document(RichDocumentFragment(), sem)
    assert context.document.body_children == []


def test_paragraph_with_rich_runs(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    sem = SemanticContext.from_processing_context(context)
    SemanticRenderer.render_to_document(
        fragment(
            paragraph("normal", bold(text("Bold")), text(" normal"), italic(text(" italic"))),
        ),
        sem,
    )
    document_xml = _document_xml_from_context(context)
    assert_contains_paragraph(document_xml, "Bold normal italic")


def test_empty_paragraph_raises():
    with pytest.raises(EmptyParagraphError):
        paragraph("normal")


def test_invalid_style_raises(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    sem = SemanticContext.from_processing_context(context)
    with pytest.raises(InvalidStyleError):
        SemanticRenderer.render_to_document(fragment(paragraph("missing.style", text("x"))), sem)


def test_javascript_hyperlink_rejected():
    with pytest.raises(InvalidHyperlinkError):
        hyperlink("javascript:alert(1)", text("bad"))


def test_fragment_composition_preserves_order(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    sem = SemanticContext.from_processing_context(context)
    first = fragment(paragraph("normal", text("First")))
    second = fragment(paragraph("normal", text("Second")))
    SemanticRenderer.render_to_document(first + second, sem)
    document_xml = _document_xml_from_context(context)
    texts = document_xml.decode("utf-8")
    assert texts.index("First") < texts.index("Second")


def test_line_break_and_field(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    context.resolved_metadata = None
    sem = SemanticContext.from_processing_context(context)
    SemanticRenderer.render_to_document(
        fragment(paragraph("normal", text("Top"), line_break(), title_field())),
        sem,
    )
    document_xml = _document_xml_from_context(context)
    assert b"w:br" in document_xml
    assert b"TITLE" in document_xml or b"Title" in document_xml


def test_bullet_list(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    context = ProcessingContext.create_default(source_dir=tmp_path)
    sem = SemanticContext.from_processing_context(context)
    SemanticRenderer.render_to_document(
        fragment(
            bullet_list(
                list_item(paragraph("normal", text("One"))),
                list_item(paragraph("normal", text("Two"))),
            )
        ),
        sem,
    )
    document_xml = _document_xml_from_context(context)
    assert_contains_paragraph(document_xml, "One")
    assert_contains_paragraph(document_xml, "Two")


def test_figure_with_image(tmp_path: Path):
    from md2docx.processor.context import ProcessingContext

    fixtures = Path(__file__).resolve().parents[2] / "fixtures"
    context = ProcessingContext.create_default(source_dir=fixtures)
    sem = SemanticContext.from_processing_context(context)
    SemanticRenderer.render_to_document(
        fragment(figure("logo.png", caption_text="Architecture", alt="Logo")),
        sem,
    )
    document_xml = _document_xml_from_context(context)
    assert b"w:drawing" in document_xml
    assert b"Architecture" in document_xml
