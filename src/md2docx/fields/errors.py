"""Dynamic field errors."""

from __future__ import annotations


class FieldError(Exception):
    """Base class for field-related errors."""


class UnknownFieldInstructionError(FieldError):
    """Field instruction is not on the supported whitelist."""


class MissingRefTargetError(FieldError):
    """REF field target bookmark does not exist."""


class InvalidFieldTargetError(FieldError):
    """Field target name is invalid."""
