"""Resolve theme tokens into StyleRegistry definitions."""

from __future__ import annotations

from md2docx.styles import semantic as S
from md2docx.styles.definition import DocumentDefaults, ParagraphStyle, RunStyle, StyleDefinition
from md2docx.styles.ooxml_ids import SEMANTIC_TO_OOXML
from md2docx.styles.registry import StyleRegistry
from md2docx.styles.tokens import ThemeTokens


class ThemeResolver:
    """Convert DocumentTheme tokens into resolved style definitions."""

    @staticmethod
    def document_defaults(tokens: ThemeTokens) -> DocumentDefaults:
        typography = tokens.typography
        return DocumentDefaults(
            font_family=typography.body_font_family,
            font_size=typography.body_font_size,
        )

    @staticmethod
    def build_registry(tokens: ThemeTokens) -> StyleRegistry:
        registry = StyleRegistry()
        for definition in ThemeResolver.build_definitions(tokens):
            registry.register(definition)
        return registry

    @staticmethod
    def build_definitions(tokens: ThemeTokens) -> tuple[StyleDefinition, ...]:
        typography = tokens.typography
        spacing = tokens.spacing
        colors = tokens.colors
        headings = tokens.headings

        normal_spacing = ParagraphStyle(
            spacing_after=spacing.paragraph_after,
            line_spacing=spacing.paragraph_line,
            line_rule=spacing.paragraph_line_rule,
        )

        def heading_run(size: int) -> RunStyle:
            run = RunStyle(bold=True, font_size=size)
            if typography.heading_font_family:
                run = RunStyle(
                    font_family=typography.heading_font_family,
                    bold=True,
                    font_size=size,
                    color=colors.heading,
                )
            elif colors.heading:
                run = RunStyle(bold=True, font_size=size, color=colors.heading)
            return run

        quote_run = RunStyle(italic=True, color=colors.quote)

        return (
            StyleDefinition(
                semantic_id=S.NORMAL,
                ooxml_id=SEMANTIC_TO_OOXML[S.NORMAL],
                name="Normal",
                ui_priority=0,
                q_format=True,
                paragraph=normal_spacing,
            ),
            StyleDefinition(
                semantic_id=S.HEADING1,
                ooxml_id=SEMANTIC_TO_OOXML[S.HEADING1],
                name="heading 1",
                based_on=S.NORMAL,
                ui_priority=9,
                q_format=True,
                paragraph=ParagraphStyle(
                    spacing_before=spacing.heading1_before,
                    spacing_after=spacing.heading1_after,
                ),
                run=heading_run(headings.heading1_size),
            ),
            StyleDefinition(
                semantic_id=S.HEADING2,
                ooxml_id=SEMANTIC_TO_OOXML[S.HEADING2],
                name="heading 2",
                based_on=S.NORMAL,
                ui_priority=9,
                q_format=True,
                paragraph=ParagraphStyle(
                    spacing_before=spacing.heading2_before,
                    spacing_after=spacing.heading2_after,
                ),
                run=heading_run(headings.heading2_size),
            ),
            StyleDefinition(
                semantic_id=S.HEADING3,
                ooxml_id=SEMANTIC_TO_OOXML[S.HEADING3],
                name="heading 3",
                based_on=S.NORMAL,
                ui_priority=9,
                q_format=True,
                paragraph=ParagraphStyle(
                    spacing_before=spacing.heading3_before,
                    spacing_after=spacing.heading3_after,
                ),
                run=heading_run(headings.heading3_size),
            ),
            StyleDefinition(
                semantic_id=S.LIST_PARAGRAPH,
                ooxml_id=SEMANTIC_TO_OOXML[S.LIST_PARAGRAPH],
                name="List Paragraph",
                based_on=S.NORMAL,
                ui_priority=34,
                q_format=True,
                paragraph=ParagraphStyle(
                    indent_left=spacing.list_indent_left,
                    contextual_spacing=True,
                ),
            ),
            StyleDefinition(
                semantic_id=S.LIST_BULLET,
                ooxml_id=SEMANTIC_TO_OOXML[S.LIST_BULLET],
                name="List Bullet",
                based_on=S.NORMAL,
                ui_priority=99,
                paragraph=ParagraphStyle(contextual_spacing=True),
            ),
            StyleDefinition(
                semantic_id=S.LIST_NUMBER,
                ooxml_id=SEMANTIC_TO_OOXML[S.LIST_NUMBER],
                name="List Number",
                based_on=S.NORMAL,
                ui_priority=99,
                paragraph=ParagraphStyle(contextual_spacing=True),
            ),
            StyleDefinition(
                semantic_id=S.QUOTE,
                ooxml_id=SEMANTIC_TO_OOXML[S.QUOTE],
                name="Quote",
                based_on=S.NORMAL,
                next_style=S.NORMAL,
                ui_priority=29,
                q_format=True,
                run=quote_run,
            ),
            StyleDefinition(
                semantic_id=S.CODE_BLOCK,
                ooxml_id=SEMANTIC_TO_OOXML[S.CODE_BLOCK],
                name="No Spacing",
                based_on=S.NORMAL,
                ui_priority=1,
                q_format=True,
                paragraph=ParagraphStyle(
                    spacing_after=spacing.code_block_after,
                    line_spacing=spacing.code_block_line,
                    line_rule=spacing.code_block_line_rule,
                ),
                run=RunStyle(
                    font_family=typography.code_block_font_family,
                    font_size=typography.code_font_size,
                    color=colors.code,
                ),
            ),
            StyleDefinition(
                semantic_id=S.INLINE_CODE,
                ooxml_id=SEMANTIC_TO_OOXML[S.INLINE_CODE],
                name="Code",
                style_type="character",
                ui_priority=99,
                run=RunStyle(
                    font_family=typography.inline_code_font_family,
                    font_size=typography.code_font_size,
                    color=colors.code,
                ),
            ),
            StyleDefinition(
                semantic_id=S.TABLE,
                ooxml_id=SEMANTIC_TO_OOXML[S.TABLE],
                name="Table Grid",
                style_type="table",
                ui_priority=59,
                q_format=True,
            ),
            StyleDefinition(
                semantic_id=S.CAPTION,
                ooxml_id=SEMANTIC_TO_OOXML[S.CAPTION],
                name="Caption",
                based_on=S.NORMAL,
                ui_priority=35,
                q_format=True,
                paragraph=ParagraphStyle(spacing_before=0, spacing_after=120),
                run=RunStyle(italic=True, font_size=18),
            ),
            StyleDefinition(
                semantic_id=S.TOC1,
                ooxml_id=SEMANTIC_TO_OOXML[S.TOC1],
                name="toc 1",
                based_on=S.NORMAL,
                ui_priority=39,
                paragraph=ParagraphStyle(spacing_after=0),
            ),
            StyleDefinition(
                semantic_id=S.TOC2,
                ooxml_id=SEMANTIC_TO_OOXML[S.TOC2],
                name="toc 2",
                based_on=S.NORMAL,
                ui_priority=39,
                paragraph=ParagraphStyle(spacing_after=0, indent_left=spacing.toc2_indent),
            ),
            StyleDefinition(
                semantic_id=S.TOC3,
                ooxml_id=SEMANTIC_TO_OOXML[S.TOC3],
                name="toc 3",
                based_on=S.NORMAL,
                ui_priority=39,
                paragraph=ParagraphStyle(spacing_after=0, indent_left=spacing.toc3_indent),
            ),
            StyleDefinition(
                semantic_id=S.DEFINITION_TERM,
                ooxml_id=SEMANTIC_TO_OOXML[S.DEFINITION_TERM],
                name="Definition Term",
                based_on=S.NORMAL,
                ui_priority=99,
                run=RunStyle(bold=True),
            ),
            StyleDefinition(
                semantic_id=S.DEFINITION_DESCRIPTION,
                ooxml_id=SEMANTIC_TO_OOXML[S.DEFINITION_DESCRIPTION],
                name="Definition Description",
                based_on=S.NORMAL,
                ui_priority=99,
                paragraph=ParagraphStyle(indent_left=spacing.list_indent_left),
            ),
            StyleDefinition(
                semantic_id=S.FOOTNOTE_TEXT,
                ooxml_id=SEMANTIC_TO_OOXML[S.FOOTNOTE_TEXT],
                name="Footnote Text",
                based_on=S.NORMAL,
                ui_priority=99,
            ),
        )
