"""Architecture boundary tests for advanced Markdown features."""

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


def test_footnote_manager_does_not_import_parser_or_markdown():
    path = SRC_ROOT / "footnotes" / "manager.py"
    forbidden_prefixes = ("md2docx.parser", "markdown")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes) or imported == "markdown"
    ]
    assert violations == []


def test_footnote_handlers_use_api_not_footnote_builder():
    path = SRC_ROOT / "elements" / "footnote_reference.py"
    forbidden = ("md2docx.ooxml.footnote", "build_footnote_reference_run")
    source = path.read_text(encoding="utf-8")
    violations = [token for token in forbidden if token in source]
    assert violations == []


def test_html_adapter_does_not_import_ooxml_or_handlers():
    path = SRC_ROOT / "parser" / "html_adapter.py"
    forbidden_prefixes = ("md2docx.ooxml", "md2docx.elements", "md2docx.processor")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []
