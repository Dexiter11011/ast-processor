"""Malformed and edge-case Markdown input."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.processor.errors import ImageNotFoundError
from md2docx.validation import validate_docx


def test_empty_markdown_produces_valid_docx(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "empty.docx"
    convert_markdown_to_docx(fixtures_dir / "empty.md", output)
    assert validate_docx(output).ok


def test_only_whitespace_produces_empty_body(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "ws.docx"
    convert_markdown_to_docx(fixtures_dir / "malformed/only-whitespace.md", output)
    assert validate_docx(output).ok


def test_unclosed_emphasis_parses_without_crash(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "bad-emphasis.docx"
    convert_markdown_to_docx(fixtures_dir / "malformed/unclosed-emphasis.md", output)
    assert validate_docx(output).ok


def test_very_long_line(tmp_path: Path):
    source = tmp_path / "long.md"
    source.write_text("x" * 10000 + "\n", encoding="utf-8")
    output = tmp_path / "long.docx"
    convert_markdown_to_docx(source, output)
    assert validate_docx(output).ok


def test_unicode_fixture(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "unicode.docx"
    convert_markdown_to_docx(fixtures_dir / "unicode.md", output)
    assert validate_docx(output).ok


def test_missing_image_is_error(tmp_path: Path, fixtures_dir: Path):
    with pytest.raises(ImageNotFoundError):
        convert_markdown_to_docx(
            fixtures_dir / "malformed/missing-image.md",
            tmp_path / "missing.docx",
        )
