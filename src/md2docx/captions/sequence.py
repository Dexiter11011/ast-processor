"""Sequence identity — maps kinds to Word SEQ names; does not count numbers."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from md2docx.captions.kinds import CaptionKind, SequenceKind
from md2docx.fields.manager import FieldManager


@dataclass
class SequenceManager:
    """Owns sequence identity and field creation — never application-level counters."""

    def sequence_kind(self, caption_kind: CaptionKind) -> SequenceKind:
        return SequenceKind.from_caption_kind(caption_kind)

    def sequence_name(self, caption_kind: CaptionKind) -> str:
        return self.sequence_kind(caption_kind).value

    def label(self, caption_kind: CaptionKind) -> str:
        return self.sequence_kind(caption_kind).label()

    def seq_field_runs(self, caption_kind: CaptionKind, fields: FieldManager) -> list[etree._Element]:
        """Build SEQ field runs for the given caption kind."""
        return fields.seq_field(self.sequence_name(caption_kind))
