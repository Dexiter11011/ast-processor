"""Alternative theme used only in tests to verify theme switching."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from md2docx.styles.definition import DocumentDefaults
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.resolver import ThemeResolver
from md2docx.styles.tokens import (
    ColorTokens,
    HeadingScaleTokens,
    ThemeTokens,
    TypographyTokens,
    default_tokens,
)


def alternative_tokens() -> ThemeTokens:
    base = default_tokens()
    return base.override(
        typography=replace(base.typography, body_font_family="Georgia", body_font_size=24),
        headings=replace(base.headings, heading1_size=40),
        colors=replace(base.colors, quote="8B4513", link="800080"),
    )


@dataclass(frozen=True)
class AlternativeTestTheme:
    """Test-only theme with distinct body, heading, quote, and link presentation."""

    tokens: ThemeTokens = field(default_factory=alternative_tokens)

    @classmethod
    def create(cls) -> AlternativeTestTheme:
        return cls()

    @property
    def document_defaults(self) -> DocumentDefaults:
        return ThemeResolver.document_defaults(self.tokens)

    def build_registry(self) -> StyleRegistry:
        return ThemeResolver.build_registry(self.tokens)
