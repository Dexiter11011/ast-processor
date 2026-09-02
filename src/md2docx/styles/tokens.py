"""Theme token model — visual configuration separate from semantic styles."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class TypographyTokens:
    body_font_family: str = "Calibri"
    body_font_size: int = 22
    heading_font_family: str | None = None
    code_block_font_family: str = "Courier New"
    inline_code_font_family: str = "Consolas"
    code_font_size: int | None = None


@dataclass(frozen=True)
class ColorTokens:
    text: str | None = None
    heading: str | None = None
    link: str = "0563C1"
    code: str | None = None
    quote: str | None = None


@dataclass(frozen=True)
class SpacingTokens:
    paragraph_after: int = 160
    paragraph_line: int = 259
    paragraph_line_rule: str = "auto"
    heading1_before: int = 240
    heading1_after: int = 120
    heading2_before: int = 200
    heading2_after: int = 120
    heading3_before: int = 200
    heading3_after: int = 120
    list_indent_left: int = 720
    toc2_indent: int = 220
    toc3_indent: int = 440
    code_block_after: int = 0
    code_block_line: int = 240
    code_block_line_rule: str = "auto"


@dataclass(frozen=True)
class HeadingScaleTokens:
    heading1_size: int = 32
    heading2_size: int = 26
    heading3_size: int = 24


@dataclass(frozen=True)
class PageDefaultsTokens:
    page_width: int = 11906
    page_height: int = 16838
    margin_top: int = 1440
    margin_right: int = 1440
    margin_bottom: int = 1440
    margin_left: int = 1440
    margin_header: int = 720
    margin_footer: int = 720
    emit_margins: bool = False
    orientation: str = "portrait"


@dataclass(frozen=True)
class LinkPresentationTokens:
    color: str = "0563C1"
    underline: str = "single"


@dataclass(frozen=True)
class TablePresentationTokens:
    border_sz: str = "4"
    border_color_single: str = "auto"
    border_color_double: str = "000000"
    cell_margin: str = "108"
    header_bold: bool = True
    header_default_align: str = "center"


@dataclass(frozen=True)
class ThemeTokens:
    typography: TypographyTokens = TypographyTokens()
    colors: ColorTokens = ColorTokens()
    spacing: SpacingTokens = SpacingTokens()
    headings: HeadingScaleTokens = HeadingScaleTokens()
    page: PageDefaultsTokens = PageDefaultsTokens()
    link: LinkPresentationTokens = LinkPresentationTokens()
    table: TablePresentationTokens = TablePresentationTokens()

    def override(self, **changes: object) -> ThemeTokens:
        """Return a copy with top-level token groups replaced."""
        return replace(self, **changes)


def default_tokens() -> ThemeTokens:
    """Built-in default token set matching the pre-iteration-15 stylesheet."""
    return ThemeTokens()


def compose_tokens(base: ThemeTokens, **group_overrides: object) -> ThemeTokens:
    """Simple theme composition: override selected token groups."""
    return base.override(**group_overrides)
