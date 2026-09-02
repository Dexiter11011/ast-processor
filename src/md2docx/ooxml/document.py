"""OOXML document accumulator."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from lxml import etree

from md2docx.ooxml import api

if TYPE_CHECKING:
    from md2docx.ast.types import Table

Element = etree._Element


class OoxmlDocument:
    """Accumulates body-level OOXML for word/document.xml."""

    def __init__(self) -> None:
        self._body_children: list[Element] = []

    @property
    def body_children(self) -> list[Element]:
        return self._body_children

    def add_body_element(self, child: Element) -> None:
        self._body_children.append(deepcopy(child))

    def add_body_elements(self, children: list[Element]) -> None:
        for child in children:
            self.add_body_element(child)

    def add_paragraph(
        self,
        runs: list[Element] | None = None,
        *,
        style_id: str | None = None,
        num_id: int | None = None,
        num_level: int = 0,
    ) -> None:
        self.add_body_element(api.paragraph(runs, style_id=style_id, num_id=num_id, num_level=num_level))

    def add_heading(self, runs: list[Element], *, style_id: str) -> None:
        self.add_body_element(api.heading(runs, style_id=style_id))

    def add_table(
        self,
        table_ast: Table,
        rows: list[list[list[Element]]],
        *,
        table_style_id: str | None = None,
        table_presentation=None,
    ) -> None:
        self.add_body_element(
            api.table(
                table_ast,
                rows,
                table_style_id=table_style_id,
                table_presentation=table_presentation,
            )
        )

    def add_horizontal_rule(self) -> None:
        self.add_body_element(api.horizontal_rule())

    def add_page_break(self) -> None:
        self.add_body_element(api.page_break())

    def add_code_block(self, value: str, *, style_id: str | None = None) -> None:
        self.add_body_element(api.code_block(value, style_id=style_id))

    def add_list_separator(self) -> None:
        self.add_body_element(api.list_separator())

    def add_table_separator(self) -> None:
        self.add_body_element(api.table_separator())

    def add_image(
        self,
        *,
        rel_id: str,
        width_emu: int,
        height_emu: int,
        doc_pr_id: int,
        name: str,
    ) -> None:
        self.add_body_element(
            api.image_paragraph(
                rel_id=rel_id,
                width_emu=width_emu,
                height_emu=height_emu,
                doc_pr_id=doc_pr_id,
                name=name,
            )
        )

    def add_alt_text(self, alt: str) -> None:
        self.add_body_element(api.alt_text_paragraph(alt))
