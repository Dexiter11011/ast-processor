"""Resolve semantic style roles to OOXML style identifiers."""

from __future__ import annotations

from dataclasses import dataclass

from md2docx.styles import semantic as S
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.theme import DefaultTheme, DocumentTheme
from md2docx.styles.tokens import LinkPresentationTokens, TablePresentationTokens


@dataclass
class StyleManager:
    """Facade over StyleRegistry for element handlers."""

    theme: DocumentTheme
    registry: StyleRegistry

    @classmethod
    def from_theme(
        cls,
        theme: DocumentTheme,
        *,
        plugin_registry=None,
    ) -> StyleManager:
        registry = theme.build_registry()
        if plugin_registry is not None:
            plugin_registry.apply_styles(registry)
        return cls(theme=theme, registry=registry)

    @classmethod
    def create_default(cls) -> StyleManager:
        return cls.from_theme(DefaultTheme.create())

    def resolve_semantic(self, role: str, *, level: int = 0) -> str:
        """Return semantic style id for a document role."""
        if role == "heading":
            return S.HEADING_BY_LEVEL.get(level, S.HEADING1)
        if role == "blockquote":
            return S.QUOTE
        if role == "code_block":
            return S.CODE_BLOCK
        if role == "list_bullet":
            return S.LIST_BULLET
        if role == "list_number":
            return S.LIST_NUMBER
        if role == "table":
            return S.TABLE
        if role == "caption":
            return S.CAPTION
        if role == "normal":
            return S.NORMAL
        return S.NORMAL

    def resolve(self, role: str, level: int = 0) -> str:
        """Return OOXML styleId for a document role (handler-facing)."""
        return self.registry.ooxml_id(self.resolve_semantic(role, level=level))

    def resolve_character(self, role: str) -> str:
        """Return OOXML character styleId for an inline role."""
        if role == "inline_code":
            return self.registry.ooxml_id(S.INLINE_CODE)
        return ""

    def to_ooxml(self, semantic_id: str) -> str:
        """Translate a semantic style id to its OOXML styleId."""
        return self.registry.ooxml_id(semantic_id)

    def link_presentation(self) -> LinkPresentationTokens:
        """Resolved hyperlink appearance from the active theme."""
        link = self.theme.tokens.link
        return LinkPresentationTokens(color=self.theme.tokens.colors.link, underline=link.underline)

    def table_presentation(self) -> TablePresentationTokens:
        """Resolved table presentation tokens from the active theme."""
        return self.theme.tokens.table

    def styles_xml(self) -> bytes:
        """Serialize styles.xml for the current registry."""
        from md2docx.ooxml.styles_xml_writer import StylesXmlWriter

        return StylesXmlWriter(document_defaults=self.theme.document_defaults).write(self.registry)
