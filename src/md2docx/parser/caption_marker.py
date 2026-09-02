"""Parser-internal AST marker for caption directives (removed by caption_transform)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from md2docx.captions.kinds import CaptionKind


@dataclass
class CaptionMarker:
    """Temporary node emitted by the Markdown parser before caption coalescing."""

    type: Literal["caption_marker"] = "caption_marker"
    kind: CaptionKind = CaptionKind.FIGURE
    text: str = ""
    line: int | None = None
