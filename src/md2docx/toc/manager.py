"""Build TOC field paragraphs via the OOXML API."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from md2docx.ooxml import api
from md2docx.toc.definition import TocSpec


@dataclass
class TocManager:
    """Owns TOC, List of Figures, and List of Tables field generation."""

    def build_paragraph(self, spec: TocSpec) -> etree._Element:
        return api.toc_field(min_level=spec.min_level, max_level=spec.max_level)

    def build_lof_paragraph(self) -> etree._Element:
        return api.lof_field()

    def build_lot_paragraph(self) -> etree._Element:
        return api.lot_field()
