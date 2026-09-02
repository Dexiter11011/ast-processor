"""Contract tests for plugin loading failures."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.plugin_api import PluginLoadError, UnsupportedApiVersionError
from md2docx.plugin_api.registry import PluginRegistry
from md2docx.plugins.loader import load_plugin, load_plugins

CONTRACTS_DIR = Path(__file__).resolve().parent


def test_missing_plugin_file(tmp_path):
    missing = tmp_path / "missing.py"
    registry = PluginRegistry.empty()
    with pytest.raises(PluginLoadError) as exc:
        load_plugin(missing, registry)
    assert exc.value.code == "plugin_load_error"


def test_syntax_error_plugin(tmp_path):
    bad = tmp_path / "bad_syntax.py"
    bad.write_text("def (\n", encoding="utf-8")
    registry = PluginRegistry.empty()
    with pytest.raises(PluginLoadError):
        load_plugin(bad, registry)


def test_missing_entrypoint(tmp_path):
    bad = tmp_path / "no_plugin.py"
    bad.write_text("VALUE = 1\n", encoding="utf-8")
    registry = PluginRegistry.empty()
    with pytest.raises(PluginLoadError):
        load_plugin(bad, registry)


def test_invalid_api_version(tmp_path):
    bad = tmp_path / "bad_version.py"
    bad.write_text(
        "from md2docx.plugin_api import PluginMetadata, PluginRegistry\n"
        "class P:\n"
        "    @property\n"
        "    def metadata(self):\n"
        "        return PluginMetadata(name='bad.version', version='1.0.0', api_version='99')\n"
        "    def register(self, registry): pass\n"
        "plugin = P()\n",
        encoding="utf-8",
    )
    registry = PluginRegistry.empty()
    with pytest.raises(PluginLoadError) as exc:
        load_plugin(bad, registry)
    assert isinstance(exc.value.__cause__, UnsupportedApiVersionError)
    assert exc.value.__cause__.code == "unsupported_api_version"


def test_valid_minimal_plugin_loads():
    source = CONTRACTS_DIR / "plugins" / "minimal_plugin.py"
    registry = load_plugins([source])
    assert registry.frozen
    assert registry.loaded_plugins[0].name == "contract.minimal"
