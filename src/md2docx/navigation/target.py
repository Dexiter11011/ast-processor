"""Semantic navigation target model."""

from __future__ import annotations

from dataclasses import dataclass

from md2docx.navigation.kinds import NavigationTargetKind


@dataclass(frozen=True)
class NavigationTarget:
    """A document navigation anchor with semantic metadata."""

    kind: NavigationTargetKind
    name: str
    bookmark_name: str
    label: str
    level: int | None = None
