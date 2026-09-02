"""Unit tests for FieldManager."""

from __future__ import annotations

import pytest

from md2docx.fields.errors import MissingRefTargetError
from md2docx.fields.manager import FieldManager
from md2docx.fields.ref_style import RefStyle
from md2docx.references.manager import BookmarkManager
from tests.helpers import W_NS


def test_field_manager_marks_dynamic_usage():
    manager = FieldManager()
    assert not manager.has_dynamic_fields
    manager.page_field()
    assert manager.has_dynamic_fields


def test_ref_field_requires_existing_bookmark():
    bookmarks = BookmarkManager()
    bookmarks.register("architecture", bookmark_id=1)
    manager = FieldManager()
    runs = manager.ref_field("architecture", bookmarks=bookmarks)
    assert len(runs) == 5

    with pytest.raises(MissingRefTargetError):
        manager.ref_field("missing", bookmarks=bookmarks)


def test_ref_field_caption_style_uses_r_and_h_switches():
    bookmarks = BookmarkManager()
    bookmarks.register("figure-architecture", bookmark_id=1)
    manager = FieldManager()
    runs = manager.ref_field(
        "figure-architecture",
        bookmarks=bookmarks,
        ref_style=RefStyle.CAPTION,
    )
    instr = runs[1].find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert "REF figure-architecture" in (instr.text or "")
    assert "\\r" in (instr.text or "")
    assert "\\h" in (instr.text or "")


def test_ref_field_heading_style_preserves_h_only():
    bookmarks = BookmarkManager()
    bookmarks.register("architecture", bookmark_id=1)
    manager = FieldManager()
    runs = manager.ref_field("architecture", bookmarks=bookmarks, ref_style=RefStyle.HEADING)
    instr = runs[1].find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert "\\r" not in (instr.text or "")
    assert "\\h" in (instr.text or "")


def test_page_field_renders_fld_simple():
    manager = FieldManager()
    element = manager.page_field()
    assert element.tag == f"{{{W_NS}}}fldSimple"
    assert element.get(f"{{{W_NS}}}instr") == " PAGE "
