"""CLI tests for --template flag."""

from __future__ import annotations

import pytest

from md2docx.cli.main import main


def test_help_shows_template_option(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "--template PATH" in output
    assert "Use an existing DOCX document as a template." in output
    assert "--title TEXT" in output
    assert "--author TEXT" in output
    assert "--date TEXT" in output
