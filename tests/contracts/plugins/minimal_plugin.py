"""Minimal plugin with empty registration."""

from __future__ import annotations

from md2docx.plugin_api import PluginMetadata, PluginRegistry


class MinimalPlugin:
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="contract.minimal", version="1.0.0")

    def register(self, registry: PluginRegistry) -> None:
        return None


plugin = MinimalPlugin()
