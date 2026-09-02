"""Semantic style identifiers — document-level roles, not OOXML styleIds."""

NORMAL = "normal"
HEADING1 = "heading1"
HEADING2 = "heading2"
HEADING3 = "heading3"
QUOTE = "quote"
CODE_BLOCK = "code_block"
INLINE_CODE = "inline_code"
LIST_PARAGRAPH = "list_paragraph"
LIST_BULLET = "list_bullet"
LIST_NUMBER = "list_number"

# Reserved for future table styling (not used in iteration 9).
TABLE = "table"
TABLE_HEADER = "table_header"
TABLE_CELL = "table_cell"
CAPTION = "caption"
TOC1 = "toc1"
TOC2 = "toc2"
TOC3 = "toc3"
DEFINITION_TERM = "definition_term"
DEFINITION_DESCRIPTION = "definition_description"
FOOTNOTE_TEXT = "footnote_text"

HEADING_BY_LEVEL = {
    1: HEADING1,
    2: HEADING2,
    3: HEADING3,
}
