"""Cross-reference semantic model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from md2docx.captions.kinds import CaptionKind


@dataclass(frozen=True)
class CrossReference:
    """Reference to an existing bookmark with optional display prefix and caption kind."""

    target: str
    kind: CaptionKind | None = None
    prefix: str = "See "
    display: str = ""
