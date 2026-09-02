"""Contract tests for public error codes."""

from __future__ import annotations

import pytest

from md2docx.plugin_api import (
    DuplicateRegistrationError,
    InvalidPluginNameError,
    PluginError,
    PluginLoadError,
    RegistryFrozenError,
    ReservedNameError,
    UnsupportedApiVersionError,
)
from md2docx.plugin_api.registry import PluginRegistry
from tests.contracts.plugins.minimal_plugin import MinimalPlugin


def test_public_errors_expose_codes():
    assert PluginLoadError("x").code == "plugin_load_error"
    assert DuplicateRegistrationError("x").code == "duplicate_registration"
    assert RegistryFrozenError("x").code == "registry_frozen"
    assert UnsupportedApiVersionError("x").code == "unsupported_api_version"
    assert InvalidPluginNameError("x").code == "invalid_plugin_name"
    assert ReservedNameError("x").code == "reserved_name"


def test_plugin_error_base_accepts_override_code():
    error = PluginError("message", code="custom")
    assert error.code == "custom"


def test_duplicate_registration_has_stable_type_and_code():
    registry = PluginRegistry.empty()
    registry.load_plugin(MinimalPlugin())
    with pytest.raises(DuplicateRegistrationError) as exc:
        registry.load_plugin(MinimalPlugin())
    assert type(exc.value) is DuplicateRegistrationError
    assert exc.value.code == "duplicate_registration"
