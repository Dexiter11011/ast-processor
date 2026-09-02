"""Facade registry for plugin extensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from md2docx.elements import create_default_registry
from md2docx.plugin_api.context import PluginContext
from md2docx.plugin_api.directive import DirectiveDefinition
from md2docx.plugin_api.errors import (
    DuplicateRegistrationError,
    RegistryFrozenError,
    UnsupportedApiVersionError,
)
from md2docx.plugin_api.metadata import PLUGIN_API_VERSION, PluginMetadata
from md2docx.plugin_api.names import (
    validate_ast_type,
    validate_placeholder_name,
    validate_plugin_name,
    validate_style_id,
)
from md2docx.plugin_api.region import TemplateRegionDefinition
from md2docx.plugin_api.validator import ValidationPhase, ValidatorDefinition
from md2docx.processor.element_handler import ElementHandler
from md2docx.processor.registry import HandlerRegistry
from md2docx.styles.definition import StyleDefinition
from md2docx.templates.placeholders import PlaceholderKind

if TYPE_CHECKING:
    from md2docx.plugin_api.plugin import Plugin


@dataclass
class PluginRegistry:
    """Composition facade over core registries and plugin extension points."""

    _frozen: bool = False
    _current_plugin: str | None = None
    _plugin_names: set[str] = field(default_factory=set)
    _handlers: dict[str, ElementHandler] = field(default_factory=dict)
    _styles: dict[str, StyleDefinition] = field(default_factory=dict)
    _directives: dict[str, DirectiveDefinition] = field(default_factory=dict)
    _regions: dict[str, TemplateRegionDefinition] = field(default_factory=dict)
    _validators: dict[str, ValidatorDefinition] = field(default_factory=dict)
    _ast_types: set[str] = field(default_factory=set)
    _plugin_placeholders: dict[str, PlaceholderKind] = field(default_factory=dict)
    _loaded_plugins: list[PluginMetadata] = field(default_factory=list)

    @classmethod
    def empty(cls) -> PluginRegistry:
        return cls()

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def loaded_plugins(self) -> tuple[PluginMetadata, ...]:
        return tuple(self._loaded_plugins)

    def _ensure_mutable(self) -> None:
        if self._frozen:
            raise RegistryFrozenError("plugin registry is frozen")

    def load_plugin(self, plugin: Plugin) -> None:
        """Validate metadata and call ``register`` on a plugin instance."""
        self._ensure_mutable()
        metadata = plugin.metadata
        validate_plugin_name(metadata.name)
        if metadata.name in self._plugin_names:
            raise DuplicateRegistrationError(f'duplicate plugin name: "{metadata.name}"')
        if metadata.api_version != PLUGIN_API_VERSION:
            raise UnsupportedApiVersionError(
                f'unsupported plugin API version: {metadata.api_version!r} '
                f'(expected {PLUGIN_API_VERSION!r})'
            )
        self._current_plugin = metadata.name
        try:
            plugin.register(self)
        finally:
            self._current_plugin = None
        self._plugin_names.add(metadata.name)
        self._loaded_plugins.append(metadata)

    def register_handler(self, node_type: str, handler: ElementHandler) -> None:
        self._ensure_mutable()
        plugin_name = self._require_plugin_context()
        validate_ast_type(node_type, plugin_name=plugin_name)
        if node_type in self._handlers or node_type in self._ast_types:
            raise DuplicateRegistrationError(f'duplicate handler registration for {node_type!r}')
        self._handlers[node_type] = handler
        self._ast_types.add(node_type)

    def register_style(self, definition: StyleDefinition) -> None:
        self._ensure_mutable()
        plugin_name = self._require_plugin_context()
        validate_style_id(definition.semantic_id, plugin_name=plugin_name)
        if definition.semantic_id in self._styles:
            raise DuplicateRegistrationError(
                f'duplicate style registration for {definition.semantic_id!r}'
            )
        self._styles[definition.semantic_id] = definition

    def register_directive(self, definition: DirectiveDefinition) -> None:
        self._ensure_mutable()
        plugin_name = self._require_plugin_context()
        if not definition.name.startswith(f"{plugin_name}."):
            raise DuplicateRegistrationError(
                f'directive {definition.name!r} must be namespaced under {plugin_name!r}'
            )
        if definition.name in self._directives:
            raise DuplicateRegistrationError(
                f'duplicate directive registration for {definition.name!r}'
            )
        self._directives[definition.name] = definition

    def register_template_region(self, definition: TemplateRegionDefinition) -> None:
        self._ensure_mutable()
        plugin_name = self._require_plugin_context()
        validate_placeholder_name(definition.placeholder_name)
        if definition.placeholder_name in self._regions:
            raise DuplicateRegistrationError(
                f'duplicate template region registration for {definition.placeholder_name!r}'
            )
        if definition.placeholder_name in self._plugin_placeholders:
            raise DuplicateRegistrationError(
                f'duplicate template region registration for {definition.placeholder_name!r}'
            )
        self._regions[definition.placeholder_name] = definition
        self._plugin_placeholders[definition.placeholder_name] = PlaceholderKind.PLUGIN

    def register_validator(self, definition: ValidatorDefinition) -> None:
        self._ensure_mutable()
        plugin_name = self._require_plugin_context()
        if not definition.name.startswith(f"{plugin_name}."):
            raise DuplicateRegistrationError(
                f'validator {definition.name!r} must be namespaced under {plugin_name!r}'
            )
        if definition.name in self._validators:
            raise DuplicateRegistrationError(
                f'duplicate validator registration for {definition.name!r}'
            )
        self._validators[definition.name] = definition

    def freeze(self) -> None:
        self._frozen = True

    def build_handler_registry(self) -> HandlerRegistry:
        registry = create_default_registry()
        for node_type, handler in self._handlers.items():
            if registry.has(node_type):
                raise DuplicateRegistrationError(
                    f'plugin handler conflicts with built-in type {node_type!r}'
                )
            registry.register(node_type, handler)
        return registry

    def apply_styles(self, registry) -> None:
        for definition in self._styles.values():
            registry.register(definition)

    def plugin_placeholder_kinds(self) -> dict[str, PlaceholderKind]:
        return dict(self._plugin_placeholders)

    def directives(self) -> tuple[DirectiveDefinition, ...]:
        return tuple(self._directives.values())

    def match_directive(self, line: str, *, line_no: int = 0) -> object | None:
        stripped = line.strip()
        for definition in self._directives.values():
            match = definition.pattern.match(stripped)
            if match is not None:
                return definition.to_ast(match, line_no)
        return None

    def region_for(self, placeholder_name: str) -> TemplateRegionDefinition | None:
        return self._regions.get(placeholder_name)

    def strip_ast_types_for_regions(self, region_names: set[str]) -> set[str]:
        strip_types: set[str] = set()
        for name in region_names:
            region = self._regions.get(name)
            if region is not None:
                strip_types.update(region.strip_ast_types)
        return strip_types

    def validators_for(self, phase: ValidationPhase) -> tuple[ValidatorDefinition, ...]:
        return tuple(item for item in self._validators.values() if item.phase is phase)

    def run_validators(self, phase: ValidationPhase, subject: object) -> None:
        for definition in self.validators_for(phase):
            definition.validate(subject)

    def _require_plugin_context(self) -> str:
        if self._current_plugin is None:
            raise RegistryFrozenError(
                "register_* may only be called from Plugin.register()"
            )
        return self._current_plugin
