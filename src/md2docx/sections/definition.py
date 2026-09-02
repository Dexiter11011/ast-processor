"""Section and page layout definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass(frozen=True)
class PageSize:
    """Page dimensions in twips (1/1440 inch)."""

    width: int
    height: int

    A4 = None  # type: ignore[misc, assignment]
    LETTER = None  # type: ignore[misc, assignment]


PageSize.A4 = PageSize(11906, 16838)
PageSize.LETTER = PageSize(12240, 15840)


@dataclass(frozen=True)
class PageMargins:
    """Page margins in twips."""

    top: int
    right: int
    bottom: int
    left: int
    header: int = 720
    footer: int = 720


# Word default ~1 inch margins
PageMargins.DEFAULT = PageMargins(1440, 1440, 1440, 1440)


@dataclass(frozen=True)
class PageLayout:
    size: PageSize
    orientation: Orientation = Orientation.PORTRAIT
    margins: PageMargins | None = None

    @classmethod
    def a4_portrait(cls, *, margins: PageMargins | None = None) -> PageLayout:
        return cls(PageSize.A4, Orientation.PORTRAIT, margins)

    @classmethod
    def a4_landscape(cls, *, margins: PageMargins | None = None) -> PageLayout:
        return cls(PageSize.A4, Orientation.LANDSCAPE, margins)

    @classmethod
    def letter_portrait(cls, *, margins: PageMargins | None = None) -> PageLayout:
        return cls(PageSize.LETTER, Orientation.PORTRAIT, margins)

    @classmethod
    def letter_landscape(cls, *, margins: PageMargins | None = None) -> PageLayout:
        return cls(PageSize.LETTER, Orientation.LANDSCAPE, margins)

    def effective_size(self) -> tuple[int, int]:
        width = self.size.width
        height = self.size.height
        if self.orientation == Orientation.LANDSCAPE and width < height:
            width, height = height, width
        return width, height


@dataclass
class Section:
    """Section-level properties (layout + optional header/footer references)."""

    layout: PageLayout
    header_rel_id: str | None = None
    footer_rel_id: str | None = None
    header_paragraphs: list = field(default_factory=list)
    footer_paragraphs: list = field(default_factory=list)
