"""Contract tests: no-plugin mode remains backward compatible."""

from __future__ import annotations

from pathlib import Path

from tests.contracts.helpers.fixture import ContractDocumentFixture
from tests.contracts.helpers.semantic_docx import assert_contains_paragraph


def test_plain_markdown_still_converts(tmp_path: Path):
    fixture = ContractDocumentFixture(tmp_path=tmp_path)
    output = fixture.convert("# Hello\n\nParagraph text.\n")
    document_xml = fixture.document_xml(output)
    assert_contains_paragraph(document_xml, "Hello")
    assert_contains_paragraph(document_xml, "Paragraph text.")
