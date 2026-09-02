"""OOXML TOC field tests."""

from md2docx.ooxml import api
from tests.helpers import W_NS


def test_toc_field_structure():
    para = api.toc_field(min_level=1, max_level=3)
    fld_chars = para.findall(f".//{{{W_NS}}}fldChar")
    instr = para.find(f".//{{{W_NS}}}instrText")
    assert len(fld_chars) == 3
    types = [el.get(f"{{{W_NS}}}fldCharType") for el in fld_chars]
    assert types == ["begin", "separate", "end"]
    assert instr is not None
    assert 'TOC \\o "1-3"' in (instr.text or "")


def test_toc_field_custom_levels():
    para = api.toc_field(min_level=2, max_level=3)
    instr = para.find(f".//{{{W_NS}}}instrText")
    assert 'TOC \\o "2-3"' in (instr.text or "")
