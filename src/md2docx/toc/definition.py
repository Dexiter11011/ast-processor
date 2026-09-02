"""TOC configuration model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TocSpec:
    """Heading level range included in the table of contents."""

    min_level: int = 1
    max_level: int = 3

    def __post_init__(self) -> None:
        if self.min_level < 1 or self.max_level < self.min_level:
            raise ValueError(
                f"invalid TOC levels: min={self.min_level}, max={self.max_level}"
            )
