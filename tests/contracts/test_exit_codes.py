"""Contract tests for CLI exit codes."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.cli.main import main


def test_success_exit_code(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Title\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    assert main([str(source), "-o", str(output)]) == 0


def test_missing_input_exit_code(tmp_path: Path):
    missing = tmp_path / "missing.md"
    assert main([str(missing)]) == 1


def test_input_directory_exit_code(tmp_path: Path):
    assert main([str(tmp_path)]) == 1


def test_processing_error_exit_code(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("![x](./missing.png)\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    assert main([str(source), "-o", str(output)]) == 2


def test_invalid_theme_exit_code(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    theme = tmp_path / "bad.yaml"
    theme.write_text("not: valid: theme\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    assert main([str(source), "--theme", str(theme), "-o", str(output)]) == 2


def test_same_input_output_exit_code(tmp_path: Path):
    source = tmp_path / "doc.md"
    source.write_text("# Hi\n", encoding="utf-8")
    assert main([str(source), "-o", str(source)]) == 1


def test_output_directory_exit_code(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    out_dir = tmp_path / "outputs"
    out_dir.mkdir()
    assert main([str(source), "-o", str(out_dir)]) == 1
