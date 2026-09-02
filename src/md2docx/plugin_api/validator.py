"""Validator extension definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class ValidationPhase(Enum):
    """When a plugin validator runs during conversion."""

    PARSE = "parse"
    SEMANTIC = "semantic"
    RENDER = "render"
    PACKAGE = "package"


ValidatorFn = Callable[[Any], None]


@dataclass(frozen=True)
class ValidatorDefinition:
    """Named validator bound to a lifecycle phase."""

    name: str
    phase: ValidationPhase
    validate: ValidatorFn
