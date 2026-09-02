"""Theme merge semantics tests."""

from __future__ import annotations

from pathlib import Path

from md2docx.styles.tokens import default_tokens
from md2docx.themes.loader import ThemeLoader


def test_partial_override_preserves_non_overridden_fields(fixtures_dir: Path):
    theme = ThemeLoader.load(fixtures_dir / "themes" / "minimal.yaml")
    defaults = default_tokens()
    assert theme.tokens.colors.heading == "111111"
    assert theme.tokens.colors.link == defaults.colors.link
    assert theme.tokens.typography.body_font_family == defaults.typography.body_font_family


def test_nested_group_merge_preserves_sibling_fields(tmp_path: Path):
    path = tmp_path / "partial-body.yaml"
    path.write_text(
        "typography:\n  body:\n    size: 12pt\n",
        encoding="utf-8",
    )
    theme = ThemeLoader.load(path)
    defaults = default_tokens()
    assert theme.tokens.typography.body_font_size == 24
    assert theme.tokens.typography.body_font_family == defaults.typography.body_font_family


def test_corporate_theme_overrides_expected_groups(fixtures_dir: Path):
    theme = ThemeLoader.load(fixtures_dir / "themes" / "corporate.yaml")
    defaults = default_tokens()
    assert theme.tokens.typography.body_font_family == "Arial"
    assert theme.tokens.colors.quote == "666666"
    assert theme.tokens.page.emit_margins is True
    assert theme.tokens.spacing.list_indent_left != defaults.spacing.list_indent_left
