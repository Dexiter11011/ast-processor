"""OOXML table builder."""

from __future__ import annotations

from copy import deepcopy

from lxml import etree

from md2docx.ast.types import Table
from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.xml_builder import W_NS, w_attr, w_element, w_tag
from md2docx.ast.table_merge import table_logical_column_count
from md2docx.styles.tokens import TablePresentationTokens

_ALIGN_VAL = {"left": "left", "center": "center", "right": "right"}
_VALIGN_VAL = {"top": "top", "center": "center", "bottom": "bottom"}
_DEFAULT_PRESENTATION = TablePresentationTokens()


def _resolve_cell_align(*, cell_align: str, column_align: str, header: bool, default_align: str) -> str:
    if cell_align:
        return cell_align
    if column_align:
        return column_align
    if header:
        return default_align
    return "left"


def _apply_bold_to_paragraph(paragraph: etree._Element) -> None:
    for run in paragraph.findall(f"{{{W_NS}}}r"):
        r_pr = run.find(w_tag("rPr"))
        if r_pr is None:
            r_pr = etree.SubElement(run, w_tag("rPr"))
            run.insert(0, r_pr)
        if r_pr.find(w_tag("b")) is None:
            etree.SubElement(r_pr, w_tag("b"))


def _apply_paragraph_align(paragraph: etree._Element, align: str) -> None:
    jc_val = _ALIGN_VAL.get(align)
    if jc_val is None:
        return
    p_pr = paragraph.find(w_tag("pPr"))
    if p_pr is None:
        p_pr = etree.SubElement(paragraph, w_tag("pPr"))
        paragraph.insert(0, p_pr)
    jc = p_pr.find(w_tag("jc"))
    if jc is None:
        jc = etree.SubElement(p_pr, w_tag("jc"))
    jc.set(w_attr("val"), jc_val)


def _add_table_borders(tbl_pr: etree._Element, borders: str, presentation: TablePresentationTokens) -> None:
    if borders == "single":
        border_val = "single"
        extra = {"sz": presentation.border_sz, "space": "0", "color": presentation.border_color_single}
    elif borders == "double":
        border_val = "double"
        extra = {"sz": presentation.border_sz, "space": "0", "color": presentation.border_color_double}
    elif borders == "none":
        border_val = "nil"
        extra = {}
    else:
        return
    borders_el = etree.SubElement(tbl_pr, w_tag("tblBorders"))
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge_el = etree.SubElement(borders_el, w_tag(edge))
        edge_el.set(w_attr("val"), border_val)
        for key, value in extra.items():
            edge_el.set(w_attr(key), value)


def _add_cell_margins(tc_pr: etree._Element, presentation: TablePresentationTokens) -> None:
    tc_mar = etree.SubElement(tc_pr, w_tag("tcMar"))
    for edge in ("top", "left", "bottom", "right"):
        margin = etree.SubElement(tc_mar, w_tag(edge))
        margin.set(w_attr("w"), presentation.cell_margin)
        margin.set(w_attr("type"), "dxa")


def _add_cell_shading(tc_pr: etree._Element, fill: str) -> None:
    shd = etree.SubElement(tc_pr, w_tag("shd"))
    shd.set(w_attr("val"), "clear")
    shd.set(w_attr("color"), "auto")
    shd.set(w_attr("fill"), fill)


def _add_cell_valign(tc_pr: etree._Element, valign: str) -> None:
    v_align_val = _VALIGN_VAL.get(valign)
    if v_align_val is None:
        return
    v_align = etree.SubElement(tc_pr, w_tag("vAlign"))
    v_align.set(w_attr("val"), v_align_val)


def _append_cell_paragraphs(
    tc: etree._Element,
    *,
    paragraphs: list[etree._Element],
    align: str,
    header: bool,
    header_bold: bool,
) -> None:
    if len(paragraphs) > 0:
        for paragraph in paragraphs:
            formatted = deepcopy(paragraph)
            _apply_paragraph_align(formatted, align)
            if header and header_bold:
                _apply_bold_to_paragraph(formatted)
            tc.append(formatted)
        return
    empty = build_paragraph([])
    _apply_paragraph_align(empty, align)
    if header and header_bold:
        _apply_bold_to_paragraph(empty)
    tc.append(empty)


def build_table(
    table: Table,
    rows: list[list[list[etree._Element]]],
    *,
    table_style_id: str | None = None,
    table_presentation: TablePresentationTokens | None = None,
) -> etree._Element:
    """Build a formatted w:tbl from AST metadata and collected cell paragraphs."""
    presentation = table_presentation or _DEFAULT_PRESENTATION
    column_count = table_logical_column_count(table.rows)
    tbl = w_element("tbl")

    tbl_pr = etree.SubElement(tbl, w_tag("tblPr"))
    if table_style_id:
        tbl_style = etree.SubElement(tbl_pr, w_tag("tblStyle"))
        tbl_style.set(w_attr("val"), table_style_id)
    tbl_w = etree.SubElement(tbl_pr, w_tag("tblW"))
    tbl_w.set(w_attr("type"), "auto")
    tbl_w.set(w_attr("w"), "0")
    _add_table_borders(tbl_pr, table.borders, presentation)

    tbl_grid = etree.SubElement(tbl, w_tag("tblGrid"))
    for _ in range(column_count):
        etree.SubElement(tbl_grid, w_tag("gridCol"))

    for row_index, row_cells in enumerate(rows):
        row_meta = table.rows[row_index] if row_index < len(table.rows) else None
        if row_meta is None:
            continue
        header = row_meta.header
        tr = etree.SubElement(tbl, w_tag("tr"))
        if header:
            tr_pr = etree.SubElement(tr, w_tag("trPr"))
            etree.SubElement(tr_pr, w_tag("tblHeader"))
        col_index = 0
        cell_index = 0
        for cell_meta in row_meta.cells:
            if col_index >= column_count:
                break
            if cell_meta.merged:
                cell_index += 1
                continue
            if cell_meta.vmerge_continue:
                tc = etree.SubElement(tr, w_tag("tc"))
                tc_pr = etree.SubElement(tc, w_tag("tcPr"))
                v_merge = etree.SubElement(tc_pr, w_tag("vMerge"))
                v_merge.set(w_attr("val"), "continue")
                tc.append(build_paragraph([]))
                col_index += 1
                cell_index += 1
                continue

            tc = etree.SubElement(tr, w_tag("tc"))
            tc_pr = etree.SubElement(tc, w_tag("tcPr"))
            _add_cell_margins(tc_pr, presentation)
            if cell_meta.colspan > 1:
                grid_span = etree.SubElement(tc_pr, w_tag("gridSpan"))
                grid_span.set(w_attr("val"), str(cell_meta.colspan))
            if cell_meta.rowspan > 1:
                etree.SubElement(tc_pr, w_tag("vMerge"))
            if cell_meta.bg:
                _add_cell_shading(tc_pr, cell_meta.bg)
            if cell_meta.valign:
                _add_cell_valign(tc_pr, cell_meta.valign)

            column_align = table.column_aligns[col_index] if col_index < len(table.column_aligns) else ""
            align = _resolve_cell_align(
                cell_align=cell_meta.align,
                column_align=column_align,
                header=header,
                default_align=presentation.header_default_align,
            )
            paragraphs = row_cells[cell_index] if cell_index < len(row_cells) else []
            _append_cell_paragraphs(
                tc,
                paragraphs=paragraphs,
                align=align,
                header=header,
                header_bold=presentation.header_bold,
            )
            col_index += max(cell_meta.colspan, 1)
            cell_index += 1
    return tbl
