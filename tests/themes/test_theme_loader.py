"""ThemeLoader unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.styles.tokens import default_tokens
from md2docx.themes.errors import ThemeLoadError, ThemeValidationError
from md2docx.themes.loader import ThemeLoader
from md2docx.themes.yaml_theme import YamlDocumentTheme


@pytest.fixture
def themes_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "themes"


def test_load_valid_full_theme(themes_dir: Path):
    theme = ThemeLoader.load(themes_dir / "corporate.yaml")
    assert isinstance(theme, YamlDocumentTheme)
    assert theme.name == "corporate"
    assert theme.tokens.typography.body_font_family == "Arial"
    assert theme.tokens.typography.body_font_size == 22
    assert theme.tokens.colors.heading == "123456"
    assert theme.tokens.headings.heading1_size == 56


def test_load_valid_minimal_theme(themes_dir: Path):
    theme = ThemeLoader.load(themes_dir / "minimal.yaml")
    defaults = default_tokens()
    assert theme.name == "minimal"
    assert theme.tokens.colors.heading == "111111"
    assert theme.tokens.typography.body_font_family == defaults.typography.body_font_family
    assert theme.tokens.spacing.paragraph_after == defaults.spacing.paragraph_after


def test_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(ThemeLoadError, match="theme file not found"):
        ThemeLoader.load(missing)


def test_empty_file(tmp_path: Path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("   \n", encoding="utf-8")
    with pytest.raises(ThemeLoadError, match="theme file is empty"):
        ThemeLoader.load(empty)


def test_invalid_yaml(tmp_path: Path):
    broken = tmp_path / "broken.yaml"
    broken.write_text("name: corporate\n  bad indent: true\n", encoding="utf-8")
    with pytest.raises(ThemeLoadError, match="invalid theme YAML"):
        ThemeLoader.load(broken)


def test_wrong_root_type(tmp_path: Path):
    path = tmp_path / "list.yaml"
    path.write_text("- item\n", encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="theme root must be a mapping"):
        ThemeLoader.load(path)


def test_unknown_top_level_field(tmp_path: Path):
    path = tmp_path / "unknown.yaml"
    path.write_text("typographi:\n  body:\n    family: Arial\n", encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="typographi unknown theme field"):
        ThemeLoader.load(path)


def test_unknown_nested_field(tmp_path: Path):
    path = tmp_path / "nested.yaml"
    path.write_text("typography:\n  body:\n    font: Arial\n", encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="typography.body.font unknown theme field"):
        ThemeLoader.load(path)


def test_wrong_type_boolean(tmp_path: Path):
    path = tmp_path / "bool.yaml"
    path.write_text('table:\n  header_bold: "yes"\n', encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="table.header_bold must be a boolean"):
        ThemeLoader.load(path)


def test_invalid_color(tmp_path: Path):
    path = tmp_path / "color.yaml"
    path.write_text("colors:\n  heading: blue\n", encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="colors.heading must be a 6-digit hex color"):
        ThemeLoader.load(path)


def test_invalid_measurement(tmp_path: Path):
    path = tmp_path / "size.yaml"
    path.write_text("typography:\n  body:\n    size: large\n", encoding="utf-8")
    with pytest.raises(ThemeValidationError, match="typography.body.size"):
        ThemeLoader.load(path)


def test_color_accepts_hash_prefix(tmp_path: Path):
    path = tmp_path / "hash.yaml"
    path.write_text("colors:\n  heading: '#123456'\n", encoding="utf-8")
    theme = ThemeLoader.load(path)
    assert theme.tokens.colors.heading == "123456"


def test_invalid_theme_fixture(themes_dir: Path):
    with pytest.raises(ThemeValidationError):
        ThemeLoader.load(themes_dir / "invalid.yaml")
