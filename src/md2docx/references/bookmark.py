"""Semantic bookmark model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    """Document-local bookmark anchor."""

    name: str
    id: int
