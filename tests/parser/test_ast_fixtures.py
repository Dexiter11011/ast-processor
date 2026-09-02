"""Parser AST snapshot tests — Markdown → AST without DOCX."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md2docx.parser.markdown_parser import MarkdownParser
from tests.ast_helpers import ast_to_dict

AST_CASES = (
    "paragraph",
    "headings",
    "emphasis",
    "links",
    "lists",
    "blockquote",
    "code",
    "images",
    "tables",
)


@pytest.fixture
def ast_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "ast"


@pytest.mark.parametrize("case", AST_CASES)
def test_parser_matches_ast_fixture(case: str, ast_fixtures_dir: Path):
    markdown = (ast_fixtures_dir / f"{case}.md").read_text(encoding="utf-8")
    expected = json.loads((ast_fixtures_dir / f"{case}.ast.json").read_text(encoding="utf-8"))
    actual = ast_to_dict(MarkdownParser().parse(markdown))
    assert actual == expected
