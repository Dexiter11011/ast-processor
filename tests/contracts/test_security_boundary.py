"""Contract tests: Markdown cannot load plugins."""

from __future__ import annotations

from pathlib import Path

from tests.contracts.helpers.fixture import ContractDocumentFixture
from tests.contracts.helpers.semantic_docx import assert_contains_paragraph, assert_not_contains_paragraph


def test_markdown_plugin_directive_is_ignored(tmp_path: Path):
    fixture = ContractDocumentFixture(tmp_path=tmp_path)
    output = fixture.convert("<!-- plugin: evil -->\n\n# Title\n")
    document_xml = fixture.document_xml(output)
    assert_contains_paragraph(document_xml, "Title")
    assert_not_contains_paragraph(document_xml, "plugin")
