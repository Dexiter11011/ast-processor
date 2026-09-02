"""Architecture boundaries for the semantic public API."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "md2docx" / "semantic"


def _public_modules() -> list[Path]:
    return [path for path in sorted(SRC.glob("*.py")) if path.name != "renderer.py"]


def test_semantic_public_modules_do_not_import_lxml():
    forbidden = ("lxml", "zipfile")
    violations = []
    for path in _public_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(forbidden):
                        violations.append(f"{path.name} imports {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith(forbidden):
                    violations.append(f"{path.name} imports {node.module}")
    assert violations == []


def test_rich_document_fragment_has_no_raw_xml_api():
    from md2docx.semantic.fragment import RichDocumentFragment

    assert not hasattr(RichDocumentFragment, "raw_xml")


def test_semantic_init_exports_no_renderer():
    import md2docx.semantic as semantic

    assert "SemanticRenderer" not in semantic.__all__
    assert "renderer" not in semantic.__all__


def test_field_kind_is_closed_enum():
    from md2docx.semantic.inline import FieldKind

    assert set(item.value for item in FieldKind) == {
        "page",
        "numpages",
        "date",
        "author",
        "title",
        "ref",
        "seq",
    }


def test_example_rich_plugin_imports_semantic_only():
    path = Path(__file__).resolve().parents[2] / "examples" / "plugins" / "rich_content_plugin.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert "md2docx.semantic" in imports
    assert not any(item.startswith("md2docx.processor") for item in imports)
    assert not any(item.startswith("md2docx.ooxml") for item in imports)
