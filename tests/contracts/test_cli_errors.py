"""Contract tests for CLI error presentation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from md2docx.cli.main import main

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def test_error_prefix_on_missing_input(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    missing = tmp_path / "missing.md"
    main([str(missing)])
    err = capsys.readouterr().err
    assert err.startswith("Error: ")
    assert "Traceback" not in err


def test_no_traceback_on_known_processing_error(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("Missing reference[^missing].", encoding="utf-8")
    main([str(source)])
    err = capsys.readouterr().err
    assert err.startswith("Error: ")
    assert "Traceback" not in err


def test_debug_shows_traceback_on_internal_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"

    def _boom(*args, **kwargs):
        raise RuntimeError("injected failure")

    monkeypatch.setattr("md2docx.cli.runner.convert_markdown_to_docx", _boom)
    code = main([str(source), "-o", str(output), "--debug"])
    err = capsys.readouterr().err
    assert code == 2
    assert "Traceback" in err


def test_internal_error_without_debug_hides_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"

    def _boom(*args, **kwargs):
        raise RuntimeError("injected failure")

    monkeypatch.setattr("md2docx.cli.runner.convert_markdown_to_docx", _boom)
    code = main([str(source), "-o", str(output)])
    err = capsys.readouterr().err
    assert code == 2
    assert err.strip() == "Error: internal error: injected failure"
    assert "Traceback" not in err


def test_input_directory_message(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    main([str(tmp_path)])
    err = capsys.readouterr().err
    assert "input path is not a file" in err


def test_same_path_message(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    source = tmp_path / "doc.md"
    source.write_text("# Hi\n", encoding="utf-8")
    main([str(source), "-o", str(source)])
    err = capsys.readouterr().err
    assert "input and output paths must differ" in err


def test_subprocess_no_traceback_on_invalid_plugin(tmp_path: Path):
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
    assert "Traceback" not in result.stderr
