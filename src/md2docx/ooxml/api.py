"""High-level OOXML API for element handlers.

Handlers should import this module instead of low-level builder modules.
All functions return lxml elements or perform document-level side effects.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union

from lxml import etree

from md2docx.ooxml.bookmark import wrap_paragraph_with_bookmark
from md2docx.ooxml.caption import build_caption_paragraph
from md2docx.ooxml.code_block import build_code_block_paragraph
from md2docx.ooxml.field import build_lof_field, build_lot_field, build_toc_field
from md2docx.ooxml.footnote import build_footnote_reference_run
from md2docx.ooxml.heading import build_heading
from md2docx.ooxml.horizontal_rule import build_horizontal_rule
from md2docx.ooxml.hyperlink import DEFAULT_LINK_COLOR, apply_link_style, build_hyperlink
from md2docx.ooxml.image import (
    build_alt_text_paragraph,
    build_image_paragraph,
    read_image_dimensions,
    scale_to_max_width,
)
from md2docx.ooxml.line_break import build_line_break_run
from md2docx.ooxml.page_break import build_page_break_paragraph
from md2docx.ooxml.paragraph import (
    build_list_separator_paragraph,
    build_paragraph,
    build_table_separator_paragraph,
)
from md2docx.ooxml.run import build_run
from md2docx.ooxml.run_format import apply_run_property
from md2docx.ooxml.run_format import run_from_formatting as _run_from_formatting
from md2docx.ooxml.table import build_table
from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import W_NS

if TYPE_CHECKING:
    from md2docx.ast.types import Table
    from md2docx.fields.manager import FieldManager
    from md2docx.fields.ref_style import RefStyle
    from md2docx.references.manager import BookmarkManager

Element = etree._Element
RunContent = Union[Element, str]


def text(value: str) -> Element:
    """Build a w:t text node."""
    return build_text(value)


def run(
    *content: RunContent,
    bold: bool = False,
    italic: bool = False,
    font: str = "",
    r_style: str = "",
) -> Element:
    """Build a w:r run, optionally wrapping text nodes."""
    children: list[Element] = []
    for item in content:
        children.append(build_text(item) if isinstance(item, str) else item)
    return build_run(children or None, bold=bold, italic=italic, font=font, r_style=r_style)


def run_from_formatting(text: str, formatting, *, r_style: str = "") -> Element:
    """Build a w:r from accumulated inline formatting state."""
    return _run_from_formatting(text, formatting, r_style=r_style)


def paragraph(
    runs: list[Element] | None = None,
    *,
    style_id: str | None = None,
    num_id: int | None = None,
    num_level: int = 0,
    indent_left_twips: int | None = None,
) -> Element:
    """Build a w:p paragraph."""
    return build_paragraph(
        runs,
        style_id=style_id,
        num_id=num_id,
        num_level=num_level,
        indent_left_twips=indent_left_twips,
    )


def heading(runs: list[Element], *, style_id: str, bookmark_name: str = "", bookmark_id: int | None = None) -> Element:
    """Build a styled heading paragraph, optionally wrapped with a bookmark."""
    para = build_heading(runs, style_id=style_id)
    if bookmark_name and bookmark_id is not None:
        return wrap_paragraph_with_bookmark(para, name=bookmark_name, bookmark_id=bookmark_id)
    return para


def hyperlink(
    runs: list[Element],
    *,
    rel_id: str | None = None,
    anchor: str | None = None,
    link_color: str | None = None,
    link_underline: str | None = None,
) -> Element:
    """Build a w:hyperlink wrapping styled runs (external rel_id or internal anchor)."""
    styled = [
        link_style(
            r,
            color=link_color if link_color is not None else DEFAULT_LINK_COLOR,
            underline=link_underline if link_underline is not None else "single",
        )
        for r in runs
    ]
    return build_hyperlink(styled, rel_id=rel_id, anchor=anchor)


def toc_field(*, min_level: int = 1, max_level: int = 3) -> Element:
    """Build a paragraph containing a Word TOC complex field."""
    return build_toc_field(min_level=min_level, max_level=max_level)


def lof_field() -> Element:
    """Build a paragraph containing a Word List of Figures field."""
    return build_lof_field()


def lot_field() -> Element:
    """Build a paragraph containing a Word List of Tables field."""
    return build_lot_field()


def page_field(fields: FieldManager) -> Element:
    """Build a PAGE dynamic field element."""
    return fields.page_field()


def numpages_field(fields: FieldManager) -> Element:
    """Build a NUMPAGES dynamic field element."""
    return fields.numpages_field()


def date_field(fields: FieldManager) -> Element:
    """Build a DATE dynamic field element."""
    return fields.date_field()


def author_field(fields: FieldManager) -> Element:
    """Build an AUTHOR dynamic field element."""
    return fields.author_field()


def title_field(fields: FieldManager) -> Element:
    """Build a TITLE dynamic field element."""
    return fields.title_field()


def ref_field(
    fields: FieldManager,
    bookmark_name: str,
    *,
    bookmarks: BookmarkManager,
    ref_style: RefStyle | None = None,
) -> list[Element]:
    """Build a REF dynamic field for an existing bookmark."""
    from md2docx.fields.ref_style import RefStyle as _RefStyle

    style = ref_style or _RefStyle.HEADING
    return fields.ref_field(bookmark_name, bookmarks=bookmarks, ref_style=style)


def seq_field(fields: FieldManager, sequence_name: str) -> list[Element]:
    """Build a SEQ dynamic field."""
    return fields.seq_field(sequence_name)


def caption_paragraph(
    *,
    label: str,
    seq_runs: list[Element],
    separator: str,
    content_runs: list[Element],
    style_id: str,
    bookmark_name: str,
    bookmark_id: int,
) -> Element:
    """Build a captioned paragraph with SEQ field and bookmark."""
    return build_caption_paragraph(
        label=label,
        seq_runs=seq_runs,
        separator=separator,
        content_runs=content_runs,
        style_id=style_id,
        bookmark_name=bookmark_name,
        bookmark_id=bookmark_id,
    )


def caption_reference_paragraph(
    fields: FieldManager,
    *,
    label: str,
    bookmark_name: str,
    bookmarks: BookmarkManager,
    prefix: str = "",
    style_id: str | None = None,
    ref_style: RefStyle | None = None,
) -> Element:
    """Build a paragraph: optional prefix + label + REF field (caption or heading style)."""
    from md2docx.fields.ref_style import RefStyle as _RefStyle

    style = ref_style or _RefStyle.CAPTION
    children: list[Element] = []
    if prefix:
        children.append(run(prefix))
    if label:
        children.append(run(label))
    children.extend(fields.ref_field(bookmark_name, bookmarks=bookmarks, ref_style=style))
    return paragraph(children, style_id=style_id)


def footer_page_numbers_paragraph(
    fields: FieldManager,
    *,
    prefix: str = "Page ",
    separator: str = " of ",
    suffix: str = "",
    style_id: str | None = None,
) -> Element:
    """Build a footer paragraph: prefix + PAGE + separator + NUMPAGES + suffix."""
    children: list[Element] = []
    if prefix:
        children.append(run(prefix))
    children.append(fields.page_field())
    if separator:
        children.append(run(separator))
    children.append(fields.numpages_field())
    if suffix:
        children.append(run(suffix))
    return paragraph(children, style_id=style_id)


def header_author_field_paragraph(fields: FieldManager, *, style_id: str | None = None) -> Element:
    """Build a header paragraph containing an AUTHOR field."""
    return paragraph([fields.author_field()], style_id=style_id)


def header_title_field_paragraph(fields: FieldManager, *, style_id: str | None = None) -> Element:
    """Build a header paragraph containing a TITLE field."""
    return paragraph([fields.title_field()], style_id=style_id)


def table(
    table_ast: Table,
    rows: list[list[list[Element]]],
    *,
    table_style_id: str | None = None,
    table_presentation=None,
) -> Element:
    """Build a w:tbl from AST metadata and collected cell paragraphs."""
    return build_table(
        table_ast,
        rows,
        table_style_id=table_style_id,
        table_presentation=table_presentation,
    )


def horizontal_rule() -> Element:
    """Build a horizontal rule paragraph."""
    return build_horizontal_rule()


def page_break() -> Element:
    """Build a page break paragraph."""
    return build_page_break_paragraph()


def code_block(value: str, *, style_id: str | None = None) -> Element:
    """Build a monospace code block paragraph."""
    return build_code_block_paragraph(value, style_id=style_id)


def list_separator() -> Element:
    """Plain separator paragraph between list blocks."""
    return build_list_separator_paragraph()


def table_separator() -> Element:
    """Plain separator paragraph after a table."""
    return build_table_separator_paragraph()


def image_paragraph(
    *,
    rel_id: str,
    width_emu: int,
    height_emu: int,
    doc_pr_id: int,
    name: str,
) -> Element:
    """Build a paragraph containing an inline picture."""
    return build_image_paragraph(
        rel_id=rel_id,
        width_emu=width_emu,
        height_emu=height_emu,
        doc_pr_id=doc_pr_id,
        name=name,
    )


def alt_text_paragraph(alt: str) -> Element:
    """Build a plain paragraph with image alt text."""
    return build_alt_text_paragraph(alt)


def image_size(data: bytes) -> tuple[int, int]:
    """Return pixel width and height for PNG/JPEG payloads."""
    return read_image_dimensions(data)


def scale_image(width_px: int, height_px: int, *, max_width_emu: int = None) -> tuple[int, int]:
    """Scale pixel dimensions to EMU for Word drawing extent."""
    if max_width_emu is None:
        return scale_to_max_width(width_px, height_px)
    return scale_to_max_width(width_px, height_px, max_width_emu=max_width_emu)


def bold(run_element: Element) -> Element:
    """Apply w:b to an existing run."""
    return apply_run_property(run_element, "b")


def italic(run_element: Element) -> Element:
    """Apply w:i to an existing run."""
    return apply_run_property(run_element, "i")


def link_style(
    run_element: Element,
    *,
    color: str = DEFAULT_LINK_COLOR,
    underline: str = "single",
) -> Element:
    """Apply default hyperlink run styling."""
    return apply_link_style(run_element, color=color, underline=underline)


def line_break() -> Element:
    """Build a w:r containing w:br for a hard line break."""
    return build_line_break_run()


def footnote_reference_run(footnote_id: int) -> Element:
    """Build a w:r containing w:footnoteReference."""
    return build_footnote_reference_run(footnote_id)


def is_active_list_paragraph(paragraph: Element) -> bool:
    """Return True if the paragraph belongs to an active Word list."""
    p_pr = paragraph.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return False
    num_pr = p_pr.find(f"{{{W_NS}}}numPr")
    if num_pr is None:
        return False
    num_id_el = num_pr.find(f"{{{W_NS}}}numId")
    if num_id_el is None:
        return False
    return num_id_el.get(f"{{{W_NS}}}val") not in (None, "0")


def media_filename(media_path: str) -> str:
    """Extract word/media filename from a package path."""
    return Path(media_path).name
