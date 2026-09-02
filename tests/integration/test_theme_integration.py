"""Theme integration tests across document features."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.styles.theme import DefaultTheme
from tests.helpers import W_NS
from tests.themes.alternative_test_theme import AlternativeTestTheme


def test_theme_integration_renders_with_both_themes(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "theme-integration.md"
    default_out = tmp_path / "default.docx"
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())

    for docx_path in (default_out, alt_out):
        with zipfile.ZipFile(docx_path, "r") as zf:
            assert "word/styles.xml" in zf.namelist()
            assert "word/document.xml" in zf.namelist()
            root = etree.fromstring(zf.read("word/document.xml"))
            assert root.findall(f".//{{{W_NS}}}p")


def test_theme_integration_styles_differ(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "theme-integration.md"
    default_out = tmp_path / "default.docx"
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())
    with zipfile.ZipFile(default_out, "r") as zf:
        default_styles = zf.read("word/styles.xml")
    with zipfile.ZipFile(alt_out, "r") as zf:
        alt_styles = zf.read("word/styles.xml")
    assert default_styles != alt_styles
