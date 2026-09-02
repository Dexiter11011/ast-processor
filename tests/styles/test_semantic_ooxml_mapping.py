"""Semantic to OOXML style id mapping tests."""

from md2docx.styles import semantic as S
from md2docx.styles.ooxml_ids import to_ooxml_id


def test_semantic_ooxml_mapping():
    assert to_ooxml_id(S.HEADING1) == "Heading1"
    assert to_ooxml_id(S.QUOTE) == "Quote"
    assert to_ooxml_id(S.CODE_BLOCK) == "NoSpacing"
    assert to_ooxml_id(S.INLINE_CODE) == "Code"
