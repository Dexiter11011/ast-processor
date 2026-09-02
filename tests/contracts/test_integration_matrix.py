"""Contract tests for basic and minimal plugins."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.content_types import build_content_types_xml
from md2docx.ooxml.relationships import RelationshipManager
from md2docx.ooxml.styles import build_minimal_styles_xml
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_tag
from md2docx.plugins.loader import load_plugins
from md2docx.templates.insertion import CONTENT_PLACEHOLDER
from md2docx.validation.package_validator import validate_docx_bytes

from tests.contracts.helpers.fixture import ContractDocumentFixture
from tests.contracts.helpers.semantic_docx import (
    assert_contains_paragraph,
    assert_has_style,
    assert_not_contains_paragraph,
)

CONTRACTS_DIR = Path(__file__).resolve().parent
BASIC_PLUGIN = CONTRACTS_DIR / "plugins" / "basic_plugin.py"
MINIMAL_PLUGIN = CONTRACTS_DIR / "plugins" / "minimal_plugin.py"
FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
THEME_PATH = FIXTURES_DIR / "themes" / "corporate.yaml"


def test_minimal_plugin_loads():
    registry = load_plugins([MINIMAL_PLUGIN])
    assert registry.loaded_plugins[0].name == "contract.minimal"


def test_basic_plugin_smoke(tmp_path: Path):
    fixture = ContractDocumentFixture(tmp_path=tmp_path, plugin_paths=[BASIC_PLUGIN])
    output = fixture.convert("<!-- callout: Contract -->\n")
    document_xml = fixture.document_xml(output)
    styles_xml = fixture.styles_xml(output)
    assert_contains_paragraph(document_xml, "Callout: Contract")
    assert_has_style(styles_xml, "ContractCallout")
    assert validate_docx_bytes(output.read_bytes()).ok


def test_basic_plugin_with_theme(tmp_path: Path):
    if not THEME_PATH.is_file():
        pytest.skip("corporate theme fixture missing")
    fixture = ContractDocumentFixture(
        tmp_path=tmp_path,
        plugin_paths=[BASIC_PLUGIN],
        theme_path=THEME_PATH,
    )
    output = fixture.convert("<!-- callout: Themed -->\n")
    document_xml = fixture.document_xml(output)
    assert_contains_paragraph(document_xml, "Callout: Themed")


def _build_template_with_region(tmp_path: Path) -> Path:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    body.append(api.paragraph([api.run("{{contract_callout}}")], style_id="Normal"))
    body.append(api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"))
    etree.SubElement(body, w_tag("sectPr"))
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    template_path = tmp_path / "contract-template.docx"
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": serialize(root),
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    template_path.write_bytes(buf.getvalue())
    return template_path


def test_basic_plugin_with_template_region(tmp_path: Path):
    template_path = _build_template_with_region(tmp_path)
    fixture = ContractDocumentFixture(
        tmp_path=tmp_path,
        plugin_paths=[BASIC_PLUGIN],
        template_path=template_path,
    )
    output = fixture.convert("<!-- callout: Body -->\n\n# Title\n")
    document_xml = fixture.document_xml(output)
    assert_contains_paragraph(document_xml, "Callout: Template region")
    assert_not_contains_paragraph(document_xml, "Callout: Body")
    assert_contains_paragraph(document_xml, "Title")


def test_integration_matrix_markdown_only(tmp_path: Path):
    fixture = ContractDocumentFixture(tmp_path=tmp_path)
    output = fixture.convert("# Matrix\n")
    assert_contains_paragraph(fixture.document_xml(output), "Matrix")


def test_integration_matrix_markdown_plugin_theme_template(tmp_path: Path):
    if not THEME_PATH.is_file():
        pytest.skip("corporate theme fixture missing")
    template_path = _build_template_with_region(tmp_path)
    fixture = ContractDocumentFixture(
        tmp_path=tmp_path,
        plugin_paths=[BASIC_PLUGIN],
        theme_path=THEME_PATH,
        template_path=template_path,
    )
    output = fixture.convert("<!-- callout: Full -->\n\n# Full\n")
    document_xml = fixture.document_xml(output)
    assert_contains_paragraph(document_xml, "Full")
    assert_contains_paragraph(document_xml, "Callout: Template region")
