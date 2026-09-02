"""Integration contract tests for rich semantic plugins."""

from __future__ import annotations

from pathlib import Path

from md2docx.plugins.loader import load_plugins
from tests.contracts.helpers.fixture import ContractDocumentFixture
from tests.contracts.helpers.semantic_docx import assert_contains_paragraph

ROOT = Path(__file__).resolve().parents[3]
RICH_PLUGIN = ROOT / "examples" / "plugins" / "rich_content_plugin.py"


def test_rich_content_plugin_renders(tmp_path: Path):
    fixture = ContractDocumentFixture(tmp_path=tmp_path, plugin_paths=[RICH_PLUGIN])
    output = fixture.convert("<!-- rich: Demo label -->\n")
    document_xml = fixture.document_xml(output)
    assert b"Rich:" in document_xml
    assert b"Demo label" in document_xml
    assert b"Example link" in document_xml


def test_notes_plugin_uses_semantic_api(tmp_path: Path):
    notes = ROOT / "examples" / "plugins" / "notes_plugin.py"
    fixture = ContractDocumentFixture(tmp_path=tmp_path, plugin_paths=[notes])
    output = fixture.convert("<!-- note: Important -->\n")
    document_xml = fixture.document_xml(output)
    assert b"Note:" in document_xml
    assert b"Important" in document_xml
