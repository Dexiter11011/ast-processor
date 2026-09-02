"""Document theme abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from md2docx.styles.definition import DocumentDefaults
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.resolver import ThemeResolver
from md2docx.styles.tokens import ThemeTokens, default_tokens


class DocumentTheme(Protocol):
    """Immutable document presentation configuration."""

    @property
    def tokens(self) -> ThemeTokens: ...

    @property
    def document_defaults(self) -> DocumentDefaults: ...

    def build_registry(self) -> StyleRegistry: ...


@dataclass(frozen=True)
class DefaultTheme:
    """Built-in document theme with the default style set."""

    tokens: ThemeTokens = field(default_factory=default_tokens)

    @classmethod
    def create(cls) -> DefaultTheme:
        return cls()

    @property
    def document_defaults(self) -> DocumentDefaults:
        return ThemeResolver.document_defaults(self.tokens)

    def build_registry(self) -> StyleRegistry:
        return ThemeResolver.build_registry(self.tokens)
