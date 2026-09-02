"""Unit tests for SequenceManager."""

from __future__ import annotations

from md2docx.captions.kinds import CaptionKind
from md2docx.captions.sequence import SequenceManager
from md2docx.fields.manager import FieldManager
from tests.helpers import W_NS


def test_sequence_manager_does_not_count():
    manager = SequenceManager()
    assert manager.sequence_name(CaptionKind.FIGURE) == "Figure"
    assert manager.sequence_name(CaptionKind.TABLE) == "Table"
    assert manager.label(CaptionKind.FIGURE) == "Figure"
    assert not hasattr(manager, "counter")
    assert not hasattr(manager, "_next_number")


def test_sequence_manager_builds_seq_fields():
    fields = FieldManager()
    manager = SequenceManager()
    runs = manager.seq_field_runs(CaptionKind.FIGURE, fields)
    assert len(runs) == 5
    instr = runs[1].find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert "SEQ Figure" in (instr.text or "")
