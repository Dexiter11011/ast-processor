"""Contract tests for atomic DOCX output."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from md2docx.cli.main import main
from md2docx.output.atomic import AtomicOutputError, AtomicOutputWriter
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx_bytes


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_atomic_writer_replaces_on_success(tmp_path: Path):
    output = tmp_path / "out.docx"
    data = b"PK\x03\x04" + b"\x00" * 20
    with AtomicOutputWriter(output) as writer:
        writer.write_bytes(data)
        writer.commit()
    assert output.read_bytes() == data
    assert not any(p.name.startswith(".out.docx.md2docx-") for p in tmp_path.iterdir())


def test_atomic_writer_aborts_on_validation_failure(tmp_path: Path):
    output = tmp_path / "out.docx"
    output.write_bytes(b"original content")
    original_hash = _sha256(output)

    with pytest.raises(AtomicOutputError, match="DOCX validation failed"):
        with AtomicOutputWriter(output, validate=True) as writer:
            writer.write_bytes(b"not a zip")
            writer.commit()

    assert _sha256(output) == original_hash
    assert not any(p.name.startswith(".out.docx.md2docx-") for p in tmp_path.iterdir())


def test_validate_flag_preserves_existing_output_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    fixtures_dir: Path,
):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "out.docx"
    output_path.write_bytes(b"keep this file")
    original_hash = _sha256(output_path)

    def _fail_validation(*args, **kwargs):
        return type("Report", (), {"ok": False, "format_messages": lambda self: "broken package"})()

    monkeypatch.setattr("md2docx.output.atomic.validate_docx_bytes", _fail_validation)
    code = main([str(input_path), "-o", str(output_path), "--validate"])
    assert code == 2
    assert _sha256(output_path) == original_hash
    assert "DOCX validation failed" in capsys.readouterr().err


def test_successful_conversion_is_valid_zip(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hello\n\nWorld.\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(source, output)
    with zipfile.ZipFile(output, "r") as zf:
        assert "word/document.xml" in zf.namelist()


def test_validate_before_commit_uses_bytes_validator(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(source, output, validate_before_commit=True)
    report = validate_docx_bytes(output.read_bytes())
    assert report.ok
