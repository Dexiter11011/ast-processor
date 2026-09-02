"""Semantic dynamic Word field model and validation."""

from md2docx.fields.errors import (
    FieldError,
    InvalidFieldTargetError,
    MissingRefTargetError,
    UnknownFieldInstructionError,
)
from md2docx.fields.kinds import FieldKind
from md2docx.fields.model import DynamicField
from md2docx.fields.parser import FieldInstructionParser

__all__ = [
    "DynamicField",
    "FieldError",
    "FieldInstructionParser",
    "FieldKind",
    "InvalidFieldTargetError",
    "MissingRefTargetError",
    "UnknownFieldInstructionError",
]

def __getattr__(name: str):
    if name == "FieldManager":
        from md2docx.fields.manager import FieldManager

        return FieldManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
