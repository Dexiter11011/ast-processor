"""Navigation and reference validation errors."""

from __future__ import annotations


class NavigationError(Exception):
    """Base class for navigation layer errors."""


class MissingNavigationTargetError(NavigationError):
    """Raised when a reference target is not registered in NavigationRegistry."""


class ReferenceKindMismatchError(NavigationError):
    """Raised when a typed cross-reference points at the wrong target kind."""
