"""Block directive extension definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DirectiveDefinition:
    """Maps a standalone HTML comment directive to an AST node."""

    name: str
    pattern: re.Pattern[str]
    to_ast: Callable[[re.Match[str], int], Any]
