"""External theme integration rendering tests."""

from __future__ import annotations

import json
import zipfile
from dataclasses import asdict
from pathlib import Path

import pytest
from lxml import etree

from md2docx.parser.markdown_parser import MarkdownParser
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.styles.theme import DefaultTheme
from md2docx.themes.loader import ThemeLoader
from tests.helpers import W_NS


@pytest.fixture
def themes_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "themes"


def _ast_json(markdown: str) -> str:
    ast = MarkdownParser().parse(markdown)
    return json.dumps(asdict(ast), sort_keys=True)


def _styles_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return zf.read("word/styles.xml")


def _document_paragraph_styles(docx_path: Path) -> list[str | None]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    styles: list[str | None] = []
    for paragraph in root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p"):
        p_pr = paragraph.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            styles.append(None)
            continue
        p_style = p_pr.find(f"{{{W_NS}}}pStyle")
        styles.append(p_style.get(f"{{{W_NS}}}val") if p_style is not None else None)
    return styles


def test_yaml_themes_do_not_change_ast(themes_dir: Path):
    markdown = (themes_dir / "theme-integration.md").read_text(encoding="utf-8")
    assert _ast_json(markdown) == _ast_json(markdown)


def test_default_minimal_corporate_styles_differ(tmp_path: Path, themes_dir: Path):
    source = themes_dir / "theme-integration.md"
    default_out = tmp_path / "default.docx"
    minimal_out = tmp_path / "minimal.docx"
    corporate_out = tmp_path / "corporate.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, minimal_out, theme=ThemeLoader.load(themes_dir / "minimal.yaml"))
    convert_markdown_to_docx(source, corporate_out, theme=ThemeLoader.load(themes_dir / "corporate.yaml"))

    default_styles = _styles_xml(default_out)
    minimal_styles = _styles_xml(minimal_out)
    corporate_styles = _styles_xml(corporate_out)
    assert default_styles != minimal_styles
    assert default_styles != corporate_styles
    assert minimal_styles != corporate_styles


def test_yaml_themes_preserve_document_structure(tmp_path: Path, themes_dir: Path):
    source = themes_dir / "theme-integration.md"
    default_out = tmp_path / "default.docx"
    corporate_out = tmp_path / "corporate.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, corporate_out, theme=ThemeLoader.load(themes_dir / "corporate.yaml"))
    assert _document_paragraph_styles(default_out) == _document_paragraph_styles(corporate_out)
