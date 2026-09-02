"""Typed navigation target kinds."""

from __future__ import annotations

from enum import Enum

from md2docx.captions.kinds import CaptionKind


class NavigationTargetKind(str, Enum):
    HEADING = "heading"
    FIGURE = "figure"
    TABLE = "table"


def caption_kind_to_navigation_kind(kind: CaptionKind) -> NavigationTargetKind:
    if kind is CaptionKind.FIGURE:
        return NavigationTargetKind.FIGURE
    return NavigationTargetKind.TABLE
