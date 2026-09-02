"""OOXML field builders — re-exports for backward compatibility."""

from md2docx.ooxml.field_renderer import (
    build_complex_field,
    build_fld_simple,
    build_lof_field,
    build_lot_field,
    build_toc_field,
)

__all__ = [
    "build_complex_field",
    "build_fld_simple",
    "build_lof_field",
    "build_lot_field",
    "build_toc_field",
]
