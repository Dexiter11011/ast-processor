"""Limited context exposed to plugins during registration."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.plugin_api.metadata import PLUGIN_API_VERSION


@dataclass(frozen=True)
class PluginContext:
    """Registration-time context for plugins."""

    api_version: str = PLUGIN_API_VERSION
    config: dict[str, str] = field(default_factory=dict)
