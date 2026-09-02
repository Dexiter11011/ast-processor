"""Plugin module loader."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from md2docx.plugin_api.errors import PluginLoadError
from md2docx.plugin_api.plugin import Plugin
from md2docx.plugin_api.registry import PluginRegistry


def _load_module(path: Path) -> ModuleType:
    if not path.is_file():
        raise PluginLoadError(f"plugin file does not exist: {path}")
    module_name = f"md2docx_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise PluginLoadError(f"unable to load plugin module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise PluginLoadError(f"plugin module failed to import: {path}: {exc}") from exc
    return module


def _find_plugin(module: ModuleType, path: Path) -> Plugin:
    candidate = getattr(module, "plugin", None)
    if candidate is None and hasattr(module, "get_plugin"):
        candidate = module.get_plugin()
    if candidate is None:
        raise PluginLoadError(f'plugin entry point not found in {path} (expected "plugin" object)')
    metadata = getattr(candidate, "metadata", None)
    if metadata is None:
        raise PluginLoadError(f'plugin in {path} is missing metadata')
    return candidate


def load_plugin(path: Path, registry: PluginRegistry) -> None:
    """Load one plugin file and register its extensions."""
    try:
        module = _load_module(path.resolve())
        plugin = _find_plugin(module, path)
        registry.load_plugin(plugin)
    except PluginLoadError:
        raise
    except Exception as exc:
        name = path.stem
        raise PluginLoadError(f'Error loading plugin "{name}": {exc}') from exc


def load_plugins(paths: list[Path]) -> PluginRegistry:
    """Load plugins in deterministic order and freeze the registry."""
    plugins: list[Plugin] = []
    for path in paths:
        module = _load_module(path.resolve())
        plugins.append(_find_plugin(module, path))
    registry = PluginRegistry.empty()
    for plugin in plugins:
        registry.load_plugin(plugin)
    registry.freeze()
    return registry
