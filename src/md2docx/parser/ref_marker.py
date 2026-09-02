"""Parser-internal AST marker for cross-reference directives (removed by caption_transform)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from md2docx.captions.kinds import CaptionKind


@dataclass
class RefMarker:
    """Temporary node emitted by the Markdown parser before caption coalescing."""

    type: Literal["ref_marker"] = "ref_marker"
    kind: CaptionKind = CaptionKind.FIGURE
    slug: str = ""
    prefix: str = "See "
    line: int | None = None
