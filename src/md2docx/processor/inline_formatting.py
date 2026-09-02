"""Rendering context and inline formatting state for AST → OOXML."""

from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class InlineFormatting:
    """Accumulated inline formatting properties for the current AST subtree."""

    bold: bool = False
    italic: bool = False
    code: bool = False
    strike: bool = False

    def with_bold(self, value: bool = True) -> InlineFormatting:
        return replace(self, bold=value)

    def with_italic(self, value: bool = True) -> InlineFormatting:
        return replace(self, italic=value)

    def with_code(self, value: bool = True) -> InlineFormatting:
        return replace(self, code=value)

    def with_strike(self, value: bool = True) -> InlineFormatting:
        return replace(self, strike=value)


@dataclass(frozen=True)
class RenderContext:
    """Current rendering state passed through inline handler recursion."""

    formatting: InlineFormatting = field(default_factory=InlineFormatting)

    @classmethod
    def default(cls) -> RenderContext:
        return cls()

    def derive(self, *, formatting: InlineFormatting | None = None) -> RenderContext:
        if formatting is None:
            return self
        return replace(self, formatting=formatting)
