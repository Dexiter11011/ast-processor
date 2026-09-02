"""Build validated dynamic fields and track document field usage."""

from __future__ import annotations

from dataclasses import dataclass, field

from lxml import etree

from md2docx.fields.errors import MissingRefTargetError
from md2docx.fields.kinds import FieldKind
from md2docx.fields.model import DynamicField
from md2docx.fields.parser import FieldInstructionParser
from md2docx.fields.ref_style import RefStyle
from md2docx.ooxml.field_renderer import FieldRenderer
from md2docx.references.manager import BookmarkManager


@dataclass
class FieldManager:
    """Owns dynamic field generation for a document conversion."""

    has_dynamic_fields: bool = field(default=False, init=False)
    _metadata_title: str | None = field(default=None, init=False, repr=False)
    _metadata_author: str | None = field(default=None, init=False, repr=False)

    def set_metadata_display(self, *, title: str | None = None, author: str | None = None) -> None:
        """Set resolved metadata values for TITLE/AUTHOR field cached display text."""
        self._metadata_title = title
        self._metadata_author = author

    def _mark_used(self) -> None:
        self.has_dynamic_fields = True

    def mark_dynamic_field_used(self) -> None:
        """Record that the document contains at least one dynamic field."""
        self._mark_used()

    def build(self, dynamic_field: DynamicField) -> list[etree._Element]:
        """Render a validated dynamic field to OOXML paragraph children."""
        self._mark_used()
        return FieldRenderer.render(
            dynamic_field,
            title_display=self._metadata_title,
            author_display=self._metadata_author,
        )

    def page_field(self) -> etree._Element:
        elements = self.build(DynamicField(kind=FieldKind.PAGE))
        return elements[0]

    def numpages_field(self) -> etree._Element:
        elements = self.build(DynamicField(kind=FieldKind.NUMPAGES))
        return elements[0]

    def date_field(self) -> etree._Element:
        elements = self.build(DynamicField(kind=FieldKind.DATE))
        return elements[0]

    def author_field(self) -> etree._Element:
        elements = self.build(DynamicField(kind=FieldKind.AUTHOR))
        return elements[0]

    def title_field(self) -> etree._Element:
        elements = self.build(DynamicField(kind=FieldKind.TITLE))
        return elements[0]

    def ref_field(
        self,
        bookmark_name: str,
        *,
        bookmarks: BookmarkManager,
        ref_style: RefStyle = RefStyle.HEADING,
    ) -> list[etree._Element]:
        FieldInstructionParser.validate_bookmark_target(bookmark_name)
        if bookmarks.resolve(bookmark_name) is None:
            raise MissingRefTargetError(
                f'REF field target bookmark "{bookmark_name}" was not found'
            )
        if ref_style is RefStyle.CAPTION:
            switches = ("\\r", "\\h")
        else:
            switches = ("\\h",)
        return self.build(
            DynamicField(kind=FieldKind.REF, target=bookmark_name, switches=switches)
        )

    def seq_field(self, sequence_name: str) -> list[etree._Element]:
        FieldInstructionParser.validate_sequence_target(sequence_name)
        return self.build(DynamicField(kind=FieldKind.SEQ, target=sequence_name))

    def parse_instruction(self, instruction: str) -> list[etree._Element]:
        """Parse a whitelisted instruction string and render OOXML."""
        return self.build(FieldInstructionParser.parse(instruction))
