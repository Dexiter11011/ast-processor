"""Contract tests for PluginRegistry behavior."""

from __future__ import annotations

import pytest

from md2docx.plugin_api import (
    DuplicateRegistrationError,
    InvalidPluginNameError,
    PluginMetadata,
    PluginRegistry,
    RegistryFrozenError,
    ReservedNameError,
)
from tests.contracts.plugins.basic_plugin import BasicPlugin
from tests.contracts.plugins.minimal_plugin import MinimalPlugin
from tests.plugins.notes_plugin import NotesPlugin


class _DummyHandler:
    def process(self, node, context, processor) -> None:
        return None


def test_registration_succeeds_and_freezes():
    registry = PluginRegistry.empty()
    registry.load_plugin(MinimalPlugin())
    registry.freeze()
    assert registry.frozen
    assert registry.loaded_plugins[0].name == "contract.minimal"


def test_duplicate_plugin_name_fails_with_code():
    registry = PluginRegistry.empty()
    registry.load_plugin(MinimalPlugin())
    with pytest.raises(DuplicateRegistrationError) as exc:
        registry.load_plugin(MinimalPlugin())
    assert exc.value.code == "duplicate_registration"


def test_duplicate_handler_in_same_plugin_fails():
    registry = PluginRegistry.empty()

    class DupHandlerPlugin:
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(name="dup.handler", version="1.0.0")

        def register(self, registry: PluginRegistry) -> None:
            registry.register_handler("dup.handler.block", _DummyHandler())
            registry.register_handler("dup.handler.block", _DummyHandler())

    with pytest.raises(DuplicateRegistrationError):
        registry.load_plugin(DupHandlerPlugin())


def test_invalid_ast_type_namespace_fails():
    registry = PluginRegistry.empty()

    class BadNamespacePlugin:
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(name="good.plugin", version="1.0.0")

        def register(self, registry: PluginRegistry) -> None:
            registry.register_handler("other.plugin.block", _DummyHandler())

    with pytest.raises(InvalidPluginNameError) as exc:
        registry.load_plugin(BadNamespacePlugin())
    assert exc.value.code == "invalid_plugin_name"


def test_reserved_ast_type_fails():
    registry = PluginRegistry.empty()

    class BadReservedPlugin:
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(name="bad.reserved", version="1.0.0")

        def register(self, registry: PluginRegistry) -> None:
            registry.register_handler("paragraph", _DummyHandler())

    with pytest.raises(ReservedNameError) as exc:
        registry.load_plugin(BadReservedPlugin())
    assert exc.value.code == "reserved_name"


def test_freeze_prevents_mutation():
    registry = PluginRegistry.empty()
    registry.load_plugin(MinimalPlugin())
    registry.freeze()
    with pytest.raises(RegistryFrozenError) as exc:
        registry.load_plugin(BasicPlugin())
    assert exc.value.code == "registry_frozen"


def test_register_outside_plugin_context_fails():
    registry = PluginRegistry.empty()
    with pytest.raises(RegistryFrozenError):
        registry.register_handler("contract.basic.callout", _DummyHandler())


def test_build_handler_registry_is_deterministic():
    first = PluginRegistry.empty()
    first.load_plugin(BasicPlugin())
    first.freeze()
    second = PluginRegistry.empty()
    second.load_plugin(BasicPlugin())
    second.freeze()
    assert first.build_handler_registry().registered_types() == second.build_handler_registry().registered_types()


def test_load_plugin_registers_notes_extensions():
    registry = PluginRegistry.empty()
    registry.load_plugin(NotesPlugin())
    assert registry.loaded_plugins[0].name == "example.notes"
    registry.freeze()
    built = registry.build_handler_registry()
    assert built.has("example.notes.note")


def test_build_handler_registry_includes_core_and_plugin_handlers():
    registry = PluginRegistry.empty()
    registry.load_plugin(NotesPlugin())
    registry.freeze()
    built = registry.build_handler_registry()
    assert built.has("example.notes.note")
    assert built.has("paragraph")


def test_match_directive_parses_note():
    registry = PluginRegistry.empty()
    registry.load_plugin(NotesPlugin())
    node = registry.match_directive("<!-- note: Important -->")
    assert getattr(node, "text", None) == "Important"
