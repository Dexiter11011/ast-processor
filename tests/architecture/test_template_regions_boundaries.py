"""Architecture boundaries for template navigation regions."""

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


def test_composer_does_not_import_parser_or_ast():
    path = SRC_ROOT / "templates" / "composer.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_composition_does_not_import_parser_or_ast():
    path = SRC_ROOT / "templates" / "composition.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_placeholder_parser_does_not_import_toc_manager():
    path = SRC_ROOT / "templates" / "placeholder_parser.py"
    forbidden_prefixes = ("md2docx.toc", "md2docx.processor")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []
