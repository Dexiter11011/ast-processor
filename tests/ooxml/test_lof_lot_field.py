"""OOXML tests for List of Figures / List of Tables fields."""

from __future__ import annotations

from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import W_NS


def test_lof_field_structure():
    para = api.lof_field()
    instr = para.find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert 'TOC \\h \\z \\c "Figure"' in (instr.text or "")


def test_lot_field_structure():
    para = api.lot_field()
    instr = para.find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert 'TOC \\h \\z \\c "Table"' in (instr.text or "")
