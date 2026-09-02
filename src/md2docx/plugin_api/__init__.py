"""Public plugin extension API for md2docx."""

from md2docx.plugin_api.context import PluginContext
from md2docx.plugin_api.directive import DirectiveDefinition
from md2docx.plugin_api.errors import (
    DuplicateRegistrationError,
    InvalidPluginNameError,
    PluginError,
    PluginLoadError,
    RegistryFrozenError,
    ReservedNameError,
    UnsupportedApiVersionError,
)
from md2docx.plugin_api.metadata import PLUGIN_API_VERSION, PluginMetadata
from md2docx.plugin_api.plugin import Plugin
from md2docx.plugin_api.region import TemplateRegionDefinition
from md2docx.plugin_api.registry import PluginRegistry
from md2docx.plugin_api.validator import ValidationPhase, ValidatorDefinition

__all__ = [
    "PLUGIN_API_VERSION",
    "DirectiveDefinition",
    "DuplicateRegistrationError",
    "InvalidPluginNameError",
    "Plugin",
    "PluginContext",
    "PluginError",
    "PluginLoadError",
    "PluginMetadata",
    "PluginRegistry",
    "RegistryFrozenError",
    "ReservedNameError",
    "TemplateRegionDefinition",
    "UnsupportedApiVersionError",
    "ValidationPhase",
    "ValidatorDefinition",
]
