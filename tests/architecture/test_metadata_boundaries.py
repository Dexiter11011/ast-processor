"""Architecture boundary tests for metadata resolution."""

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


def test_metadata_resolver_does_not_import_ooxml_or_templates():
    metadata_root = SRC_ROOT / "metadata"
    forbidden_prefixes = ("md2docx.ooxml", "md2docx.templates", "zipfile")
    violations: list[str] = []
    for path in sorted(metadata_root.rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes) or imported == "zipfile":
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_core_props_does_not_import_cli_or_parser():
    path = SRC_ROOT / "ooxml" / "core_props.py"
    forbidden_prefixes = ("md2docx.cli", "md2docx.parser")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_themes_package_does_not_import_metadata():
    forbidden_prefixes = ("md2docx.metadata",)
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "themes").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_template_composer_does_not_import_metadata_resolver():
    path = SRC_ROOT / "templates" / "composer.py"
    forbidden = ("md2docx.metadata.resolver", "MetadataResolver", "resolve_document_metadata")
    source = path.read_text(encoding="utf-8")
    violations = [token for token in forbidden if token in source]
    assert violations == []
