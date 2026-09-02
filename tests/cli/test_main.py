"""CLI UX tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from md2docx.cli.main import _build_parser, main


def test_help_shows_usage(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "usage: md2docx" in output
    assert "-o OUTPUT, --output OUTPUT" in output
    assert "--version" in output
    assert "md2docx input.md" in output


def test_version(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert re.fullmatch(r"md2docx \d+\.\d+\.\d+", capsys.readouterr().out.strip())


def test_parser_requires_input():
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_missing_input_file_reports_clear_error(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    missing = tmp_path / "document.md"
    code = main([str(missing)])
    assert code == 1
    assert capsys.readouterr().err.strip() == f"Error: input file does not exist: {missing}"


def test_undefined_footnote_reports_clear_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    input_path = tmp_path / "notes.md"
    input_path.write_text("Missing reference[^missing].", encoding="utf-8")

    code = main([str(input_path)])
    assert code == 2
    assert "undefined footnote: missing" in capsys.readouterr().err


def test_default_output_name(tmp_path: Path, fixtures_dir: Path):
    source = fixtures_dir / "hello-world.md"
    dest_input = tmp_path / "hello-world.md"
    dest_input.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    output_path = tmp_path / "hello-world.docx"

    code = main([str(dest_input)])
    assert code == 0
    assert output_path.is_file()


def test_explicit_output_path(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "custom.docx"

    code = main([str(input_path), "-o", str(output_path)])
    assert code == 0
    assert output_path.is_file()


def test_validate_flag_runs_package_validation(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "hello-world.docx"
    code = main([str(input_path), "-o", str(output_path), "--validate"])
    assert code == 0
    assert output_path.is_file()


def test_validate_flag_fails_on_invalid_docx(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "bad.docx"
    output_path.write_bytes(b"preserve me")
    original = output_path.read_bytes()

    def _fail_validation(data: bytes):
        return type("Report", (), {"ok": False, "format_messages": lambda self: "broken package"})()

    monkeypatch.setattr("md2docx.output.atomic.validate_docx_bytes", _fail_validation)
    code = main([str(input_path), "-o", str(output_path), "--validate"])
    assert code == 2
    assert "DOCX validation failed" in capsys.readouterr().err
    assert output_path.read_bytes() == original


def test_missing_image_reports_clear_error(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    md = tmp_path / "doc.md"
    md.write_text("![x](./missing.png)\n", encoding="utf-8")
    out = tmp_path / "doc.docx"
    code = main([str(md), "-o", str(out)])
    assert code == 2
    assert "image not found" in capsys.readouterr().err
