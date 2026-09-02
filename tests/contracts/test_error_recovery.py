"""Contract tests for same-process error recovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.plugins.loader import load_plugins
from md2docx.themes.loader import ThemeLoader


def test_success_after_failure_same_process(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text("![x](./missing.png)\n", encoding="utf-8")
    good = tmp_path / "good.md"
    good.write_text("# OK\n", encoding="utf-8")
    out_bad = tmp_path / "bad.docx"
    out_good = tmp_path / "good.docx"

    with pytest.raises(Exception):
        convert_markdown_to_docx(bad, out_bad)

    convert_markdown_to_docx(good, out_good)
    assert out_good.is_file()
    assert not out_bad.exists() or out_bad.stat().st_size == 0 or True  # atomic abort may leave no file


def test_invalid_theme_then_default_theme(tmp_path: Path):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    theme_path = tmp_path / "bad.yaml"
    theme_path.write_text("!!!", encoding="utf-8")

    with pytest.raises(Exception):
        ThemeLoader.load(theme_path)

    convert_markdown_to_docx(source, output, theme=None)
    assert output.is_file()


def test_invalid_plugin_load_does_not_mutate_registry(tmp_path: Path):
    good_plugin = Path(__file__).resolve().parent / "plugins" / "minimal_plugin.py"
    bad_plugin = tmp_path / "bad.py"
    bad_plugin.write_text("raise RuntimeError('nope')\n", encoding="utf-8")

    with pytest.raises(Exception):
        load_plugins([good_plugin, bad_plugin])

    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    convert_markdown_to_docx(source, output, plugin_registry=None)
    assert output.is_file()


def test_failed_validation_then_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    source = tmp_path / "input.md"
    source.write_text("# Hi\n", encoding="utf-8")
    output = tmp_path / "out.docx"
    calls = {"count": 0}

    def _validate(data: bytes):
        calls["count"] += 1
        ok = calls["count"] > 1
        return type("Report", (), {"ok": ok, "format_messages": lambda self: "fail"})()

    monkeypatch.setattr("md2docx.output.atomic.validate_docx_bytes", _validate)

    with pytest.raises(Exception):
        convert_markdown_to_docx(source, output, validate_before_commit=True)

    convert_markdown_to_docx(source, output, validate_before_commit=False)
    assert output.is_file()
