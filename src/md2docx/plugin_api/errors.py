"""Public plugin API errors."""

from __future__ import annotations


class PluginError(Exception):
    """Base class for plugin API errors."""

    code: str | None = None

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class PluginLoadError(PluginError):
    """Raised when a plugin module cannot be loaded or registered."""

    code = "plugin_load_error"


class DuplicateRegistrationError(PluginError):
    """Raised when an extension is registered more than once."""

    code = "duplicate_registration"


class RegistryFrozenError(PluginError):
    """Raised when register() is called after the registry was frozen."""

    code = "registry_frozen"


class UnsupportedApiVersionError(PluginError):
    """Raised when a plugin declares an unsupported API version."""

    code = "unsupported_api_version"


class InvalidPluginNameError(PluginError):
    """Raised when a plugin identifier fails validation."""

    code = "invalid_plugin_name"


class ReservedNameError(PluginError):
    """Raised when a plugin tries to register a reserved core name."""

    code = "reserved_name"
