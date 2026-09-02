"""Typed semantic kinds for captions and sequences."""

from __future__ import annotations

from enum import Enum


class CaptionKind(str, Enum):
    FIGURE = "figure"
    TABLE = "table"


class SequenceKind(str, Enum):
    """Canonical Word SEQ identifier names."""

    FIGURE = "Figure"
    TABLE = "Table"

    @classmethod
    def from_caption_kind(cls, kind: CaptionKind) -> SequenceKind:
        if kind is CaptionKind.FIGURE:
            return cls.FIGURE
        return cls.TABLE

    def label(self) -> str:
        """Display label token for cross-references (localization hook)."""
        return self.value
