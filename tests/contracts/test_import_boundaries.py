"""Contract plugin import boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_PREFIXES = (
    "md2docx.processor",
    "md2docx.parser",
    "md2docx.templates.merger",
    "md2docx.templates.composer",
    "md2docx.ooxml.paragraph",
    "md2docx.ooxml.run",
    "lxml",
)

ALLOWED_PREFIXES = (
    "md2docx.plugin_api",
    "md2docx.styles.definition",
    "md2docx.ooxml",
    "md2docx.ooxml.api",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return {item for item in imports if item != "__future__"}


def test_basic_plugin_uses_public_imports_only():
    path = Path(__file__).resolve().parent / "plugins" / "basic_plugin.py"
    imports = _imports(path)
    violations = [
        item
        for item in imports
        if item.startswith(FORBIDDEN_PREFIXES)
    ]
    assert violations == []
    assert any(item.startswith("md2docx.plugin_api") for item in imports)


def test_minimal_plugin_uses_plugin_api_only():
    path = Path(__file__).resolve().parent / "plugins" / "minimal_plugin.py"
    imports = _imports(path)
    assert imports == {"md2docx.plugin_api"}
