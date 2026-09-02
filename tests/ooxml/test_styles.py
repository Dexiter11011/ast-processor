"""styles.xml generator tests."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.style_ids import CODE, CODE_BLOCK, CODE_BLOCK_FONT, HEADING1, INLINE_CODE_FONT, QUOTE
from md2docx.ooxml.styles import build_minimal_styles_xml
from tests.helpers import W_NS


def _style_by_id(root: etree._Element, style_id: str):
    for style in root.findall(f"{{{W_NS}}}style"):
        if style.get(f"{{{W_NS}}}styleId") == style_id:
            return style
    return None


def test_styles_define_heading_quote_and_code():
    root = etree.fromstring(build_minimal_styles_xml())

    heading1 = _style_by_id(root, HEADING1)
    assert heading1 is not None
    assert heading1.get(f"{{{W_NS}}}type") == "paragraph"
    assert heading1.find(f".//{{{W_NS}}}b") is not None
    assert heading1.find(f".//{{{W_NS}}}sz").get(f"{{{W_NS}}}val") == "32"

    quote = _style_by_id(root, QUOTE)
    assert quote.find(f".//{{{W_NS}}}i") is not None

    code_block = _style_by_id(root, CODE_BLOCK)
    fonts = code_block.find(f".//{{{W_NS}}}rFonts")
    assert fonts.get(f"{{{W_NS}}}ascii") == CODE_BLOCK_FONT

    code = _style_by_id(root, CODE)
    assert code.get(f"{{{W_NS}}}type") == "character"
    inline_fonts = code.find(f".//{{{W_NS}}}rFonts")
    assert inline_fonts.get(f"{{{W_NS}}}ascii") == INLINE_CODE_FONT
