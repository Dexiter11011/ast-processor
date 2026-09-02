"""Parser AST snapshot tests for navigation Markdown DSL."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.ast_helpers import ast_to_dict
from tests.navigation_markdown_helpers import parse_navigation_markdown

NAVIGATION_AST_CASES = (
    "figure",
    "table-caption",
    "figure-reference",
    "table-reference",
    "heading-reference",
    "toc",
    "list-of-figures",
    "list-of-tables",
    "mixed-navigation",
    "forward-reference",
    "navigation-dsl",
)


@pytest.fixture
def navigation_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "markdown" / "navigation"


@pytest.fixture
def update_ast_golden(request: pytest.FixtureRequest) -> bool:
    return os.environ.get("UPDATE_AST_GOLDEN", "").lower() in {"1", "true", "yes"}


@pytest.mark.parametrize("case", NAVIGATION_AST_CASES)
def test_navigation_markdown_matches_ast_fixture(
    case: str,
    navigation_fixtures_dir: Path,
    update_ast_golden: bool,
):
    markdown = (navigation_fixtures_dir / f"{case}.md").read_text(encoding="utf-8")
    actual = ast_to_dict(parse_navigation_markdown(markdown))
    expected_path = navigation_fixtures_dir / f"{case}.ast.json"
    if update_ast_golden:
        expected_path.write_text(json.dumps(actual, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        pytest.skip(f"updated AST golden {expected_path.name}")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert actual == expected
