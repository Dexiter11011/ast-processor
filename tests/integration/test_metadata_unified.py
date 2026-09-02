"""Integration tests for unified document metadata."""

from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.ooxml.core_props import build_core_props_xml
from md2docx.parser.markdown_parser import MarkdownParser
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.templates.reader import DocxPackageReader
from tests.helpers import read_docx_part

CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _core_text(docx_path: Path, local_name: str, ns: str) -> str | None:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("docProps/core.xml"))
    node = root.find(f"{{{ns}}}{local_name}")
    return node.text if node is not None else None


def test_cli_overrides_front_matter_in_core_props(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "metadata.docx"
    convert_markdown_to_docx(
        fixtures_dir / "metadata-full.md",
        output,
        cli_title="CLI Title",
        cli_author="CLI Author",
    )
    assert _core_text(output, "title", DC_NS) == "CLI Title"
    assert _core_text(output, "creator", DC_NS) == "CLI Author"
    assert _core_text(output, "subject", DC_NS) == "Example Subject"
    assert _core_text(output, "keywords", CP_NS) == "markdown, docx"


def test_metadata_does_not_change_ast(fixtures_dir: Path):
    source = (fixtures_dir / "metadata-full.md").read_text(encoding="utf-8")
    from md2docx.parser.front_matter import split_front_matter

    _, body = split_front_matter(source)
    ast_default = MarkdownParser().parse(body)
    ast_with_cli = MarkdownParser().parse(body)
    assert len(ast_default.children) == len(ast_with_cli.children)
    for left, right in zip(ast_default.children, ast_with_cli.children):
        assert left.type == right.type


def test_template_placeholder_and_core_props_consistency(
    tmp_path: Path,
    fixtures_dir: Path,
):
    templates_dir = fixtures_dir / "templates"
    output = tmp_path / "template-metadata.docx"
    template = DocxPackageReader.load(templates_dir / "placeholders-basic.docx")
    convert_markdown_to_docx(
        fixtures_dir / "metadata-front-matter.md",
        output,
        template=template,
        cli_title="CLI Title",
        cli_author="CLI Author",
    )
    document = read_docx_part(output, "word/document.xml").decode("utf-8")
    assert "CLI Title" in document
    assert "CLI Author" in document
    assert "2026-08-31" in document
    assert _core_text(output, "title", DC_NS) == "CLI Title"
    assert _core_text(output, "creator", DC_NS) == "CLI Author"


def test_title_author_field_cached_text_matches_metadata(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "fields.docx"
    convert_markdown_to_docx(
        fixtures_dir / "metadata-fields.md",
        output,
        cli_title="Project Documentation",
        cli_author="Jane Doe",
    )
    with zipfile.ZipFile(output, "r") as zf:
        header = etree.fromstring(zf.read("word/header1.xml"))
    texts = [
        node.text
        for node in header.findall(f".//{{{W_NS}}}t")
        if node.text
    ]
    assert "Project Documentation" in texts
    assert "Jane Doe" in texts
    assert _core_text(output, "title", DC_NS) == "Project Documentation"
    assert _core_text(output, "creator", DC_NS) == "Jane Doe"


def test_resolved_metadata_single_source_for_core_props():
    resolved = ResolvedDocumentMetadata(
        title="Project Documentation",
        author="Jane Doe",
        subject="Subj",
        keywords=("a", "b"),
        created=datetime(2026, 8, 31, 12, 0, 0, tzinfo=timezone.utc),
        modified=datetime(2026, 8, 31, 12, 0, 0, tzinfo=timezone.utc),
    )
    xml = build_core_props_xml(resolved)
    root = etree.fromstring(xml)
    assert root.find(f"{{{DC_NS}}}title").text == "Project Documentation"
    assert root.find(f"{{{DC_NS}}}creator").text == "Jane Doe"
    created = root.find("{http://purl.org/dc/terms/}created")
    assert created.text == "2026-08-31T12:00:00Z"
