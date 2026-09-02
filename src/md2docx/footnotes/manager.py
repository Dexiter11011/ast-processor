"""Footnote registration and OOXML body assembly."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from lxml import etree

from md2docx.ast.types import BlockNode, FootnoteDefinition
from md2docx.footnotes.errors import DuplicateFootnoteError, MissingFootnoteError
from md2docx.ooxml.footnote import build_footnote_reference_run
from md2docx.styles import semantic as S

if TYPE_CHECKING:
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext


@dataclass
class FootnoteManager:
    """Register footnote labels and collect rendered footnote bodies."""

    _label_to_id: dict[str, int] = field(default_factory=dict)
    _next_id: int = 1
    _bodies: dict[int, list[etree._Element]] = field(default_factory=dict)
    has_footnotes: bool = field(default=False, init=False)

    def register_definitions(
        self,
        definitions: list[FootnoteDefinition],
        relationships=None,
    ) -> None:
        for definition in definitions:
            if definition.label in self._label_to_id:
                raise DuplicateFootnoteError(definition.label)
            footnote_id = self._next_id
            self._next_id += 1
            self._label_to_id[definition.label] = footnote_id
            self.has_footnotes = True
        if relationships is not None and self.has_footnotes:
            from md2docx.ooxml.relationships import FOOTNOTES_REL_TYPE

            if not any(r.rel_type == FOOTNOTES_REL_TYPE for r in relationships.relationships):
                relationships.add_footnotes_relationship()

    def footnote_id(self, label: str) -> int:
        try:
            return self._label_to_id[label]
        except KeyError as exc:
            raise MissingFootnoteError(label) from exc

    def footnote_reference(self, label: str) -> etree._Element:
        return build_footnote_reference_run(self.footnote_id(label))

    def render_bodies(
        self,
        definitions: list[FootnoteDefinition],
        processor: AstProcessor,
        context: ProcessingContext,
    ) -> None:
        for definition in definitions:
            footnote_id = self.footnote_id(definition.label)
            paragraphs = self._render_definition_blocks(definition.children, processor, context)
            self._bodies[footnote_id] = paragraphs

    def _render_definition_blocks(
        self,
        blocks: list[BlockNode],
        processor: AstProcessor,
        context: ProcessingContext,
    ) -> list[etree._Element]:
        saved_body = list(context.document.body_children)
        saved_block_style = context.block_style
        context.document.body_children.clear()
        context.block_style = S.FOOTNOTE_TEXT
        try:
            for block in blocks:
                processor.process(block, context)
            return list(context.document.body_children)
        finally:
            context.document.body_children.clear()
            context.document.body_children.extend(saved_body)
            context.block_style = saved_block_style

    def footnote_paragraphs(self) -> dict[int, list[etree._Element]]:
        return dict(self._bodies)
