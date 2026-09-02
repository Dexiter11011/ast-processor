"""Contract tests for CLI behavior."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from md2docx.cli.main import _build_parser, main

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
CONTRACTS_DIR = Path(__file__).resolve().parent


def test_help_includes_plugin_option():
    parser = _build_parser()
    help_text = parser.format_help()
    assert "--plugin" in help_text
    assert "PATH" in help_text


def test_plugin_option_is_repeatable():
    parser = _build_parser()
    args = parser.parse_args(["input.md", "--plugin", "a.py", "--plugin", "b.py"])
    assert args.plugin == [Path("a.py"), Path("b.py")]


def test_missing_input_exit_code(tmp_path):
    missing = tmp_path / "missing.md"
    assert main([str(missing)]) == 1


def test_invalid_plugin_exit_code(tmp_path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    bad = tmp_path / "bad.py"
    bad.write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "md2docx.cli.main",
            str(source),
            "--plugin",
            str(bad),
            "-o",
            str(output),
        ],
        cwd=str(ROOT),
        env={"PYTHONPATH": str(SRC), **dict(__import__("os").environ)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Error:" in result.stderr


def test_successful_conversion_exit_code(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Title\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    assert main([str(source), "-o", str(output)]) == 0


def test_output_directory_rejected(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    out_dir = tmp_path / "outputs"
    out_dir.mkdir()
    assert main([str(source), "-o", str(out_dir)]) == 1


def test_same_input_output_rejected(tmp_path: Path):
    source = tmp_path / "doc.md"
    source.write_text("# Hi\n", encoding="utf-8")
    assert main([str(source), "-o", str(source)]) == 1
