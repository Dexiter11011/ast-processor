"""Convert theme page tokens into section layout objects."""

from __future__ import annotations

from md2docx.sections.definition import Orientation, PageLayout, PageMargins, PageSize
from md2docx.styles.tokens import PageDefaultsTokens


def page_layout_from_tokens(tokens: PageDefaultsTokens) -> PageLayout:
    """Build the default section page layout from theme page tokens."""
    size = PageSize(tokens.page_width, tokens.page_height)
    margins = None
    if tokens.emit_margins:
        margins = PageMargins(
            top=tokens.margin_top,
            right=tokens.margin_right,
            bottom=tokens.margin_bottom,
            left=tokens.margin_left,
            header=tokens.margin_header,
            footer=tokens.margin_footer,
        )
    orientation = (
        Orientation.LANDSCAPE
        if tokens.orientation.strip().lower() == "landscape"
        else Orientation.PORTRAIT
    )
    return PageLayout(size, orientation, margins)
