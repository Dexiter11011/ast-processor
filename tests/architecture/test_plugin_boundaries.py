"""Architecture boundaries for the plugin API."""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "md2docx"


def _module_imports(module_path: Path) -> set[str]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_plugin_api_does_not_import_parser_internals():
    forbidden = ("md2docx.parser.markdown_parser", "zipfile")
    violations = []
    for path in sorted((SRC_ROOT / "plugin_api").glob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(tuple(forbidden)):
                violations.append(f"{path.name} imports {imported}")
    assert violations == []


def test_example_plugin_uses_semantic_api():
    path = Path(__file__).resolve().parents[2] / "examples" / "plugins" / "notes_plugin.py"
    imports = _module_imports(path)
    assert "md2docx.semantic" in imports
    forbidden_prefixes = (
        "md2docx.ooxml.paragraph",
        "md2docx.ooxml.run",
        "md2docx.processor",
        "md2docx.parser",
        "lxml",
    )
    violations = [item for item in imports if item.startswith(forbidden_prefixes)]
    assert violations == []


def test_contract_basic_plugin_uses_public_imports_only():
    path = Path(__file__).resolve().parents[1] / "contracts" / "plugins" / "basic_plugin.py"
    imports = _module_imports(path)
    forbidden_prefixes = (
        "md2docx.processor",
        "md2docx.parser",
        "md2docx.templates.merger",
        "lxml",
    )
    violations = [item for item in imports if item.startswith(forbidden_prefixes)]
    assert violations == []
