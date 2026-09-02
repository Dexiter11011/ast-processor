"""Table cell merge helpers (AST-level, independent of Markdown parsing)."""

from __future__ import annotations

from dataclasses import replace

from md2docx.ast.types import TableCell, TableRow


def apply_horizontal_merge(cells: list[TableCell]) -> list[TableCell]:
    """Extend colspan when an empty cell follows a non-merge anchor cell."""
    merged: list[TableCell] = []
    for cell in cells:
        if cell.vmerge_continue:
            merged.append(cell)
            continue
        if not _cell_has_content(cell):
            anchor_index = len(merged) - 1
            while anchor_index >= 0 and merged[anchor_index].merged:
                anchor_index -= 1
            if anchor_index >= 0 and not merged[anchor_index].vmerge_continue:
                anchor = merged[anchor_index]
                merged[anchor_index] = replace(anchor, colspan=anchor.colspan + 1)
                merged.append(TableCell(merged=True))
                continue
        merged.append(cell)
    return merged


def apply_vertical_merge(rows: list[TableRow]) -> list[TableRow]:
    if not rows:
        return rows
    grid: list[list[TableCell]] = [list(row.cells) for row in rows]
    for row_index in range(len(grid)):
        for col_index in range(len(grid[row_index])):
            cell = grid[row_index][col_index]
            if not cell.vmerge_continue:
                continue
            for prev_row in range(row_index - 1, -1, -1):
                if col_index >= len(grid[prev_row]):
                    continue
                anchor = grid[prev_row][col_index]
                if anchor.merged or anchor.vmerge_continue:
                    continue
                grid[prev_row][col_index] = replace(anchor, rowspan=anchor.rowspan + 1)
                break
    return [replace(row, cells=grid[index]) for index, row in enumerate(rows)]


def table_logical_column_count(rows: list[TableRow]) -> int:
    width = 0
    for row in rows:
        row_width = 0
        for cell in row.cells:
            if cell.merged:
                continue
            row_width += max(cell.colspan, 1)
        width = max(width, row_width)
    return max(width, 1)


def _cell_has_content(cell: TableCell) -> bool:
    for block in cell.children:
        if block.type == "paragraph":
            for inline in block.children:
                if inline.type == "text" and inline.value.strip():
                    return True
                if inline.type != "text":
                    return True
        else:
            return True
    return False
