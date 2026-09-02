"""Unit tests for FieldInstructionParser."""

from __future__ import annotations

import pytest

from md2docx.fields.errors import InvalidFieldTargetError, UnknownFieldInstructionError
from md2docx.fields.kinds import FieldKind
from md2docx.fields.parser import FieldInstructionParser


@pytest.mark.parametrize(
    ("instruction", "kind"),
    [
        ("PAGE", FieldKind.PAGE),
        (" NUMPAGES ", FieldKind.NUMPAGES),
        ("DATE", FieldKind.DATE),
        ("AUTHOR", FieldKind.AUTHOR),
        ("TITLE", FieldKind.TITLE),
    ],
)
def test_parse_simple_fields(instruction: str, kind: FieldKind):
    field = FieldInstructionParser.parse(instruction)
    assert field.kind is kind


def test_parse_ref_field():
    field = FieldInstructionParser.parse("REF architecture \\h")
    assert field.kind is FieldKind.REF
    assert field.target == "architecture"


def test_parse_seq_field():
    field = FieldInstructionParser.parse("SEQ Figure")
    assert field.kind is FieldKind.SEQ
    assert field.target == "Figure"


@pytest.mark.parametrize(
    "instruction",
    [
        "EXEC malicious",
        "MACRO something",
        "REF",
        "PAGE extra",
        "UNKNOWN",
        "REF bad!",
    ],
)
def test_rejects_invalid_instructions(instruction: str):
    with pytest.raises((UnknownFieldInstructionError, InvalidFieldTargetError)):
        FieldInstructionParser.parse(instruction)
