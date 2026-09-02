"""Mapping from semantic style IDs to Word OOXML styleIds."""

from __future__ import annotations

from md2docx.styles import semantic as S

SEMANTIC_TO_OOXML: dict[str, str] = {
    S.NORMAL: "Normal",
    S.HEADING1: "Heading1",
    S.HEADING2: "Heading2",
    S.HEADING3: "Heading3",
    S.QUOTE: "Quote",
    S.CODE_BLOCK: "NoSpacing",
    S.INLINE_CODE: "Code",
    S.LIST_PARAGRAPH: "ListParagraph",
    S.LIST_BULLET: "ListBullet",
    S.LIST_NUMBER: "ListNumber",
    S.TABLE: "TableGrid",
    S.CAPTION: "Caption",
    S.TOC1: "TOC1",
    S.TOC2: "TOC2",
    S.TOC3: "TOC3",
    S.DEFINITION_TERM: "DefinitionTerm",
    S.DEFINITION_DESCRIPTION: "DefinitionDescription",
    S.FOOTNOTE_TEXT: "FootnoteText",
}


def to_ooxml_id(semantic_id: str) -> str:
    try:
        return SEMANTIC_TO_OOXML[semantic_id]
    except KeyError as exc:
        raise KeyError(f"unknown semantic style: {semantic_id}") from exc
