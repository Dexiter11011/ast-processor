"""DefaultTheme tests."""

from md2docx.styles import semantic as S
from md2docx.styles.theme import DefaultTheme


def test_default_theme_registers_required_styles():
    registry = DefaultTheme.create().build_registry()
    required = (
        S.NORMAL,
        S.HEADING1,
        S.HEADING2,
        S.HEADING3,
        S.QUOTE,
        S.CODE_BLOCK,
        S.INLINE_CODE,
        S.LIST_PARAGRAPH,
        S.LIST_BULLET,
        S.LIST_NUMBER,
        S.CAPTION,
    )
    for semantic_id in required:
        assert registry.has(semantic_id), semantic_id


def test_default_theme_ooxml_mapping():
    registry = DefaultTheme.create().build_registry()
    assert registry.ooxml_id(S.CODE_BLOCK) == "NoSpacing"
    assert registry.ooxml_id(S.INLINE_CODE) == "Code"
