"""Unified processing context for element handlers."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Protocol

from md2docx.captions.service import CaptionService
from md2docx.navigation.reference import ReferenceManager
from md2docx.navigation.registry import NavigationRegistry
from md2docx.ooxml.document import OoxmlDocument
from md2docx.fields.manager import FieldManager
from md2docx.footnotes.manager import FootnoteManager
from md2docx.ooxml.numbering import NumberingManager
from md2docx.ooxml.relationships import RelationshipManager
from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.processor.inline_formatting import RenderContext
from md2docx.processor.media_manager import MediaManager
from md2docx.processor.style_manager import StyleManager
from md2docx.references.manager import BookmarkManager
from md2docx.sections.manager import SectionManager
from md2docx.processor.theme_layout import page_layout_from_tokens
from md2docx.styles import semantic as S
from md2docx.styles.theme import DefaultTheme, DocumentTheme
from md2docx.toc.manager import TocManager

if TYPE_CHECKING:
    from lxml import etree


class ProcessingInfrastructure(Protocol):
    """Shared resources that every handler receives through context (spec §8)."""

    document: OoxmlDocument
    relationships: RelationshipManager
    styles: StyleManager
    numbering: NumberingManager
    media: MediaManager
    sections: SectionManager


@dataclass
class ProcessingContext:
    """
    Unified context passed to every element handler.

    Handlers must not construct their own ``RelationshipManager``, ``MediaManager``,
    or other shared resources — they are created once here and accessed via
    ``context.document``, ``context.relationships``, etc.

    Fields below ``source_dir`` are transient walk state (list/table/inline
    collection) and may be extended in future iterations.
    """

    # Shared infrastructure
    document: OoxmlDocument
    relationships: RelationshipManager
    styles: StyleManager
    numbering: NumberingManager
    media: MediaManager
    sections: SectionManager
    bookmarks: BookmarkManager
    navigation: NavigationRegistry
    references: ReferenceManager
    toc: TocManager
    fields: FieldManager
    captions: CaptionService
    footnotes: FootnoteManager

    # Transient handler state
    run_collector: list[etree._Element] | None = None
    render_context: RenderContext = field(default_factory=RenderContext.default)
    list_style: str | None = None
    list_ordered: bool | None = None
    list_num_id: int | None = None
    list_level: int = 0
    block_style: str | None = None
    paragraph_indent_twips: int | None = None
    source_dir: Path = field(default_factory=Path.cwd)
    in_table_cell: bool = False
    table_collector: list[list[list[etree._Element]]] | None = None
    table_row_collector: list[list[etree._Element]] | None = None
    table_cell_collector: list[etree._Element] | None = None
    task_checkbox_pending: bool | None = None
    template_mode: bool = False
    resolved_metadata: ResolvedDocumentMetadata | None = None

    @classmethod
    def create_default(
        cls,
        *,
        source_dir: Path | None = None,
        theme: DocumentTheme | None = None,
        plugin_registry=None,
    ) -> ProcessingContext:
        """Build a fresh context with all shared managers wired together."""
        active_theme = theme or DefaultTheme.create()
        relationships = RelationshipManager()
        relationships.add_styles_relationship()
        styles = StyleManager.from_theme(active_theme, plugin_registry=plugin_registry)
        bookmarks = BookmarkManager()
        navigation = NavigationRegistry()
        return cls(
            document=OoxmlDocument(),
            relationships=relationships,
            styles=styles,
            numbering=NumberingManager(list_paragraph_style_id=styles.to_ooxml(S.LIST_PARAGRAPH)),
            media=MediaManager(),
            sections=SectionManager(
                relationships=relationships,
                default_layout=page_layout_from_tokens(active_theme.tokens.page),
            ),
            bookmarks=bookmarks,
            navigation=navigation,
            references=ReferenceManager(navigation=navigation, bookmarks=bookmarks),
            toc=TocManager(),
            fields=FieldManager(),
            captions=CaptionService(),
            footnotes=FootnoteManager(),
            source_dir=source_dir or Path.cwd(),
        )

    @classmethod
    def create_for_template(
        cls,
        *,
        source_dir: Path | None = None,
        theme: DocumentTheme | None = None,
        plugin_registry=None,
    ) -> ProcessingContext:
        """Build a context for rendering Markdown content into a DOCX template."""
        context = cls.create_default(
            source_dir=source_dir,
            theme=theme,
            plugin_registry=plugin_registry,
        )
        return ProcessingContext(
            document=context.document,
            relationships=context.relationships,
            styles=context.styles,
            numbering=context.numbering,
            media=context.media,
            sections=context.sections,
            bookmarks=context.bookmarks,
            navigation=context.navigation,
            references=context.references,
            toc=context.toc,
            fields=context.fields,
            captions=context.captions,
            footnotes=context.footnotes,
            source_dir=context.source_dir,
            template_mode=True,
        )

    @contextmanager
    def push_render_context(self, render_context: RenderContext) -> Generator[None, None, None]:
        """Temporarily replace render_context; restore on exit to prevent formatting leakage."""
        previous = self.render_context
        self.render_context = render_context
        try:
            yield
        finally:
            self.render_context = previous
