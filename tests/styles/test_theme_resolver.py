"""Theme resolver unit tests."""

from md2docx.styles import semantic as S
from md2docx.styles.resolver import ThemeResolver
from md2docx.styles.theme import DefaultTheme
from md2docx.styles.tokens import default_tokens


def test_resolver_builds_all_semantic_styles():
    registry = ThemeResolver.build_registry(default_tokens())
    for semantic_id in (
        S.NORMAL,
        S.HEADING1,
        S.HEADING2,
        S.HEADING3,
        S.QUOTE,
        S.CODE_BLOCK,
        S.INLINE_CODE,
        S.LIST_PARAGRAPH,
        S.TABLE,
    ):
        assert registry.has(semantic_id)


def test_resolver_document_defaults_from_tokens():
    defaults = ThemeResolver.document_defaults(default_tokens())
    assert defaults.font_family == "Calibri"
    assert defaults.font_size == 22


def test_default_theme_registry_matches_resolver():
    theme = DefaultTheme.create()
    direct = ThemeResolver.build_registry(theme.tokens)
    assert theme.build_registry().ooxml_id(S.HEADING1) == direct.ooxml_id(S.HEADING1)
