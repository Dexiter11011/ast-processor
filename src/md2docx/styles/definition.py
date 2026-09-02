"""Style definition model for document-level presentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StyleType = Literal["paragraph", "character", "table"]


@dataclass(frozen=True)
class DocumentDefaults:
    """Default run properties applied via w:docDefaults."""

    font_family: str = "Calibri"
    font_size: int = 22


@dataclass(frozen=True)
class ParagraphStyle:
    """Paragraph-level formatting for a style definition."""

    spacing_before: int | None = None
    spacing_after: int | None = None
    line_spacing: int | None = None
    line_rule: str | None = None
    indent_left: int | None = None
    contextual_spacing: bool = False


@dataclass(frozen=True)
class RunStyle:
    """Run-level formatting for a style definition."""

    font_family: str | None = None
    font_size: int | None = None
    bold: bool = False
    italic: bool = False
    color: str | None = None


@dataclass(frozen=True)
class StyleDefinition:
    """Immutable description of one document style."""

    semantic_id: str
    ooxml_id: str
    name: str
    style_type: StyleType = "paragraph"
    based_on: str | None = None
    next_style: str | None = None
    ui_priority: int | None = None
    q_format: bool = False
    paragraph: ParagraphStyle | None = None
    run: RunStyle | None = None
