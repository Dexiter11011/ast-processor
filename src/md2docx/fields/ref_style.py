"""REF field presentation styles."""

from __future__ import annotations

from enum import Enum


class RefStyle(str, Enum):
    """Controls which REF field switches are emitted."""

    HEADING = "heading"
    CAPTION = "caption"
