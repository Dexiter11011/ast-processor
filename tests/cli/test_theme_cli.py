"""CLI tests for external theme support."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md2docx.cli.main import main


@pytest.fixture
def themes_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "themes"


def test_help_shows_theme_option(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "--theme PATH" in output
    assert "Use external YAML document theme." in output


def test_no_theme_uses_default_behavior(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "hello-world.docx"
    code = main([str(source), "-o", str(output_path)])
    assert code == 0
    assert output_path.is_file()


def test_theme_path_after_input(tmp_path: Path, fixtures_dir: Path, themes_dir: Path):
    source = fixtures_dir / "hello-world.md"
    theme = themes_dir / "corporate.yaml"
    output_path = tmp_path / "corporate.docx"
    code = main([str(source), "--theme", str(theme), "-o", str(output_path)])
    assert code == 0
    with zipfile.ZipFile(output_path, "r") as zf:
        styles = zf.read("word/styles.xml").decode("utf-8")
    assert "Arial" in styles


def test_theme_path_before_input(tmp_path: Path, fixtures_dir: Path, themes_dir: Path):
    source = fixtures_dir / "hello-world.md"
    theme = themes_dir / "corporate.yaml"
    output_path = tmp_path / "corporate.docx"
    code = main(["--theme", str(theme), str(source), "-o", str(output_path)])
    assert code == 0
    assert output_path.is_file()


def test_missing_theme_reports_clear_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
):
    source = fixtures_dir / "hello-world.md"
    missing_theme = tmp_path / "missing.yaml"
    code = main([str(source), "--theme", str(missing_theme)])
    assert code == 2
    assert capsys.readouterr().err.strip() == f"Error: theme file not found: {missing_theme}"


def test_invalid_theme_reports_clear_error(
    capsys: pytest.CaptureFixture[str],
    fixtures_dir: Path,
    themes_dir: Path,
    tmp_path: Path,
):
    source = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "out.docx"
    code = main(
        [
            str(source),
            "--theme",
            str(themes_dir / "invalid.yaml"),
            "-o",
            str(output_path),
        ]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "Error: invalid theme:" in err
    assert "unknown theme field" in err


def test_minimal_theme_changes_heading_color(tmp_path: Path, fixtures_dir: Path, themes_dir: Path):
    source = fixtures_dir / "headings.md"
    output_path = tmp_path / "minimal.docx"
    code = main([str(source), "--theme", str(themes_dir / "minimal.yaml"), "-o", str(output_path)])
    assert code == 0
    with zipfile.ZipFile(output_path, "r") as zf:
        styles = zf.read("word/styles.xml").decode("utf-8")
    assert "111111" in styles
