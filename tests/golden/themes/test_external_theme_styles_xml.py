"""Golden tests for YAML-loaded external themes."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.ooxml.styles_xml_writer import StylesXmlWriter
from md2docx.themes.loader import ThemeLoader
from tests.golden.xml_compare import assert_document_xml_equal


@pytest.fixture
def themes_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "themes"


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "expected" / "themes"


def test_minimal_yaml_theme_styles_xml_matches_golden(themes_dir: Path, expected_dir: Path):
    theme = ThemeLoader.load(themes_dir / "minimal.yaml")
    actual = StylesXmlWriter(document_defaults=theme.document_defaults).write(theme.build_registry())
    expected_path = expected_dir / "minimal_theme.styles.xml"
    assert expected_path.is_file()
    assert_document_xml_equal(expected_path.read_bytes(), actual)


def test_corporate_yaml_theme_styles_xml_matches_golden(themes_dir: Path, expected_dir: Path):
    theme = ThemeLoader.load(themes_dir / "corporate.yaml")
    actual = StylesXmlWriter(document_defaults=theme.document_defaults).write(theme.build_registry())
    expected_path = expected_dir / "corporate_theme.styles.xml"
    assert expected_path.is_file()
    assert_document_xml_equal(expected_path.read_bytes(), actual)
