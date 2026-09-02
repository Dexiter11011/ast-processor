"""Theme token model tests."""

from dataclasses import replace

from md2docx.styles.tokens import TypographyTokens, compose_tokens, default_tokens


def test_default_tokens_are_immutable():
    tokens = default_tokens()
    updated = compose_tokens(tokens, typography=replace(tokens.typography, body_font_family="Inter"))
    assert tokens.typography.body_font_family == "Calibri"
    assert updated.typography.body_font_family == "Inter"


def test_compose_tokens_preserves_unmodified_groups():
    base = default_tokens()
    composed = compose_tokens(base, typography=TypographyTokens(body_font_family="Arial"))
    assert composed.colors.link == base.colors.link
