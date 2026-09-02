"""Architecture boundary tests for navigation layer."""

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


def test_navigation_registry_does_not_import_ooxml():
    path = SRC_ROOT / "navigation" / "registry.py"
    forbidden = ("md2docx.ooxml",)
    violations = [imp for imp in _module_imports(path) if imp.startswith(forbidden)]
    assert violations == []


def test_bookmark_manager_does_not_import_navigation():
    path = SRC_ROOT / "references" / "manager.py"
    forbidden = ("md2docx.navigation", "md2docx.toc")
    violations = [imp for imp in _module_imports(path) if imp.startswith(forbidden)]
    assert violations == []


def test_field_manager_does_not_import_parser():
    path = SRC_ROOT / "fields" / "manager.py"
    forbidden = ("md2docx.parser",)
    violations = [imp for imp in _module_imports(path) if imp.startswith(forbidden)]
    assert violations == []


def test_template_merger_does_not_import_captions():
    path = SRC_ROOT / "templates" / "merger.py"
    forbidden = ("md2docx.captions",)
    violations = [imp for imp in _module_imports(path) if imp.startswith(forbidden)]
    assert violations == []


def test_parser_does_not_import_ooxml():
    parser_dir = SRC_ROOT / "parser"
    forbidden = ("md2docx.ooxml",)
    violations: list[str] = []
    for path in parser_dir.glob("*.py"):
        for imp in _module_imports(path):
            if imp.startswith(forbidden):
                violations.append(f"{path.name} imports {imp}")
    assert violations == []


def test_caption_transform_does_not_import_ooxml():
    path = SRC_ROOT / "parser" / "caption_transform.py"
    forbidden = ("md2docx.ooxml", "md2docx.fields")
    violations = [imp for imp in _module_imports(path) if imp.startswith(forbidden)]
    assert violations == []
