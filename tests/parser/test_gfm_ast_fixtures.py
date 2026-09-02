"""GFM AST snapshot tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md2docx.parser.markdown_parser import MarkdownParser
from tests.ast_helpers import ast_to_dict

GFM_AST_CASES = (
    "task-list",
    "strikethrough",
    "autolinks",
    "hard-breaks",
    "escaped-markdown",
    "unicode-gfm",
    "nested-gfm",
)


@pytest.fixture
def gfm_ast_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "markdown" / "gfm"


@pytest.mark.parametrize("case", GFM_AST_CASES)
def test_gfm_parser_matches_ast_fixture(case: str, gfm_ast_dir: Path):
    markdown = (gfm_ast_dir / f"{case}.md").read_text(encoding="utf-8")
    expected = json.loads((gfm_ast_dir / f"{case}.ast.json").read_text(encoding="utf-8"))
    actual = ast_to_dict(MarkdownParser().parse(markdown))
    assert actual == expected
