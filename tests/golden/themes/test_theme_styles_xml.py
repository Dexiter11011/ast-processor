"""Golden tests for theme-specific styles.xml output."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.ooxml.styles_xml_writer import StylesXmlWriter
from md2docx.styles.theme import DefaultTheme
from tests.golden.xml_compare import assert_document_xml_equal
from tests.themes.alternative_test_theme import AlternativeTestTheme


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "expected" / "themes"


def test_default_theme_styles_xml_matches_golden(expected_dir: Path):
    theme = DefaultTheme.create()
    actual = StylesXmlWriter(document_defaults=theme.document_defaults).write(theme.build_registry())
    expected_path = expected_dir / "default_theme.styles.xml"
    assert expected_path.is_file()
    assert_document_xml_equal(expected_path.read_bytes(), actual)


def test_alternative_theme_styles_xml_matches_golden(expected_dir: Path):
    theme = AlternativeTestTheme.create()
    actual = StylesXmlWriter(document_defaults=theme.document_defaults).write(theme.build_registry())
    expected_path = expected_dir / "alternative_theme.styles.xml"
    assert expected_path.is_file()
    assert_document_xml_equal(expected_path.read_bytes(), actual)
