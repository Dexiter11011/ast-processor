"""Plugin metadata model."""

from __future__ import annotations

from dataclasses import dataclass

PLUGIN_API_VERSION = "1"


@dataclass(frozen=True)
class PluginMetadata:
    """Metadata describing a loaded plugin."""

    name: str
    version: str
    api_version: str = PLUGIN_API_VERSION
    description: str = ""
