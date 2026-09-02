"""Public semantic composition context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.semantic.fragment import RichDocumentFragment

if TYPE_CHECKING:
    from md2docx.processor.context import ProcessingContext
    from md2docx.processor.style_manager import StyleManager


@dataclass(frozen=True)
class SemanticStyles:
    """Style resolution facade for plugins."""

    _styles: StyleManager

    def to_ooxml(self, semantic_id: str) -> str:
        return self._styles.to_ooxml(semantic_id)

    def resolve(self, role: str, *, level: int = 0) -> str:
        return self._styles.resolve(role, level)


@dataclass(frozen=True)
class SemanticContext:
    """Public runtime facade over the internal processing context."""

    _processing: ProcessingContext
    metadata: ResolvedDocumentMetadata | None = None

    @property
    def styles(self) -> SemanticStyles:
        return SemanticStyles(self._processing.styles)

    @property
    def source_dir(self):
        return self._processing.source_dir

    def render(self, content: RichDocumentFragment) -> None:
        if content.empty:
            return
        from md2docx.semantic.renderer import SemanticRenderer

        SemanticRenderer.render_to_document(content, self)

    def render_elements(self, content: RichDocumentFragment):
        if content.empty:
            return []
        from md2docx.semantic.renderer import SemanticRenderer

        return SemanticRenderer.render(content, self)

    @classmethod
    def from_processing_context(
        cls,
        context: ProcessingContext,
        *,
        metadata: ResolvedDocumentMetadata | None = None,
    ) -> SemanticContext:
        resolved = metadata or getattr(context, "resolved_metadata", None)
        return cls(_processing=context, metadata=resolved)
