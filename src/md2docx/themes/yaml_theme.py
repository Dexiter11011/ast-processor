"""YAML-backed DocumentTheme implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.styles.definition import DocumentDefaults
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.resolver import ThemeResolver
from md2docx.styles.tokens import ThemeTokens, default_tokens


@dataclass(frozen=True)
class YamlDocumentTheme:
    """Document theme loaded from an external YAML configuration file."""

    name: str
    tokens: ThemeTokens = field(default_factory=default_tokens)

    @property
    def document_defaults(self) -> DocumentDefaults:
        return ThemeResolver.document_defaults(self.tokens)

    def build_registry(self) -> StyleRegistry:
        return ThemeResolver.build_registry(self.tokens)
