"""Security tests for dynamic fields."""

from __future__ import annotations

import pytest

from md2docx.fields.errors import UnknownFieldInstructionError
from md2docx.fields.parser import FieldInstructionParser
from md2docx.templates.context import DocumentContext
from md2docx.templates.context_builder import document_context_to_metadata
from md2docx.ooxml.core_props import build_core_props_xml


def test_metadata_title_is_not_field_instruction():
    context = DocumentContext(title="REF malicious")
    xml = build_core_props_xml(document_context_to_metadata(context)).decode("utf-8")
    assert "REF malicious" in xml
    assert "<w:instr" not in xml


def test_parser_rejects_exec_instruction():
    with pytest.raises(UnknownFieldInstructionError):
        FieldInstructionParser.parse("EXEC cmd")
