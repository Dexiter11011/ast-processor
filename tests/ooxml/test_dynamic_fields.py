"""OOXML dynamic field renderer tests."""

from __future__ import annotations

from md2docx.fields.kinds import FieldKind
from md2docx.fields.model import DynamicField
from md2docx.ooxml.field_renderer import FieldRenderer
from tests.helpers import W_NS


def test_render_page_as_fld_simple():
    elements = FieldRenderer.render(DynamicField(kind=FieldKind.PAGE))
    assert len(elements) == 1
    assert elements[0].tag == f"{{{W_NS}}}fldSimple"


def test_render_ref_as_complex_field():
    elements = FieldRenderer.render(
        DynamicField(kind=FieldKind.REF, target="architecture", switches=("\\h",))
    )
    assert len(elements) == 5
    instr = elements[1].find(f".//{{{W_NS}}}instrText")
    assert instr is not None
    assert "REF architecture" in (instr.text or "")
