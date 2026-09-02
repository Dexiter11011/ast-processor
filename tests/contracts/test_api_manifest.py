"""Contract test: public API manifest matches declared exports."""

from __future__ import annotations

import importlib
import json
from enum import Enum
from pathlib import Path

import md2docx.plugin_api as plugin_api
import md2docx.semantic as semantic

MANIFEST_PATH = Path(__file__).resolve().parent / "api_manifest.json"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _kind_for(name: str, value: object) -> str:
    if name == "Plugin":
        return "protocol"
    if name == "PLUGIN_API_VERSION":
        return "constant"
    if isinstance(value, type):
        if issubclass(value, Exception):
            return "exception"
        if issubclass(value, Enum):
            return "enum"
        return "class"
    return "constant"


def _actual_tier_a() -> list[dict[str, str]]:
    symbols = []
    for name in plugin_api.__all__:
        value = getattr(plugin_api, name)
        symbols.append({"name": name, "kind": _kind_for(name, value)})
    return symbols


def test_manifest_api_version_matches_constant():
    manifest = _load_manifest()
    assert manifest["api_version"] == plugin_api.PLUGIN_API_VERSION


def test_tier_a_manifest_matches_plugin_api_all():
    manifest = _load_manifest()
    expected = manifest["tier_a"]["symbols"]
    actual = _actual_tier_a()
    assert [item["name"] for item in actual] == [item["name"] for item in expected]
    assert actual == expected


def test_tier_b_symbols_are_importable():
    manifest = _load_manifest()
    for module_entry in manifest["tier_b"]["modules"]:
        module = importlib.import_module(module_entry["module"])
        for symbol in module_entry["symbols"]:
            assert hasattr(module, symbol["name"]), (
                f'{module_entry["module"]}.{symbol["name"]} missing'
            )


def test_plugin_api_does_not_export_loader():
    assert "load_plugins" not in plugin_api.__all__


def test_semantic_public_surface_matches_all():
    manifest = _load_manifest()
    semantic_entry = next(item for item in manifest["tier_b"]["modules"] if item["module"] == "md2docx.semantic")
    exported = set(semantic.__all__)
    for symbol in semantic_entry["symbols"]:
        assert symbol["name"] in exported
    assert "SemanticRenderer" not in exported
