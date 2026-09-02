"""Plugin interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from md2docx.plugin_api.metadata import PluginMetadata

if TYPE_CHECKING:
    from md2docx.plugin_api.registry import PluginRegistry


class Plugin(Protocol):
    """Extension entry point loaded by the CLI or programmatic callers."""

    @property
    def metadata(self) -> PluginMetadata: ...

    def register(self, registry: PluginRegistry) -> None: ...
