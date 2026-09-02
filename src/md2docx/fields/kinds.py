"""Supported dynamic Word field kinds."""

from __future__ import annotations

from enum import Enum


class FieldKind(Enum):
    """Semantic kinds of supported dynamic Word fields."""

    PAGE = "PAGE"
    NUMPAGES = "NUMPAGES"
    DATE = "DATE"
    AUTHOR = "AUTHOR"
    TITLE = "TITLE"
    REF = "REF"
    SEQ = "SEQ"
