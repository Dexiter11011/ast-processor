"""Validate dynamic Word field instructions in OOXML parts."""

from __future__ import annotations

import re

from lxml import etree

from md2docx.fields.parser import FieldInstructionParser
from md2docx.ooxml.xml_builder import W_NS, w_attr

_ALLOWED_SIMPLE = frozenset({"PAGE", "NUMPAGES", "DATE", "AUTHOR", "TITLE"})
_REF_INSTR_RE = re.compile(r"^\s*REF\s+([A-Za-z][A-Za-z0-9_\-]{0,39})(?:\s+\\.+)?\s*$", re.IGNORECASE)
_SEQ_INSTR_RE = re.compile(r"^\s*SEQ\s+([A-Za-z][A-Za-z0-9 ]{1,40})\s*$", re.IGNORECASE)
_TOC_INSTR_RE = re.compile(r"^\s*TOC\b", re.IGNORECASE)


def collect_bookmark_names(root: etree._Element) -> set[str]:
    names: set[str] = set()
    for start in root.findall(f".//{{{W_NS}}}bookmarkStart"):
        name = start.get(w_attr("name"))
        if name:
            names.add(name)
    return names


def validate_fields_in_part(
    root: etree._Element,
    *,
    part_name: str,
    bookmark_names: set[str],
    report,
) -> None:
    for fld in root.findall(f".//{{{W_NS}}}fldSimple"):
        instruction = fld.get(w_attr("instr")) or ""
        _validate_instruction(
            instruction,
            part_name=part_name,
            bookmark_names=bookmark_names,
            report=report,
        )

    for instr in root.findall(f".//{{{W_NS}}}instrText"):
        instruction = instr.text or ""
        _validate_instruction(
            instruction,
            part_name=part_name,
            bookmark_names=bookmark_names,
            report=report,
        )


def _validate_instruction(
    instruction: str,
    *,
    part_name: str,
    bookmark_names: set[str],
    report,
) -> None:
    normalized = " ".join(instruction.strip().split())
    if not normalized:
        report.add("fields", "empty field instruction", part=part_name)
        return

    upper = normalized.upper()
    if _TOC_INSTR_RE.match(normalized):
        return

    if upper in _ALLOWED_SIMPLE:
        try:
            FieldInstructionParser.parse(normalized)
        except Exception as exc:
            report.add("fields", str(exc), part=part_name)
        return

    ref_match = _REF_INSTR_RE.match(normalized)
    if ref_match:
        target = ref_match.group(1)
        try:
            FieldInstructionParser.validate_bookmark_target(target)
        except Exception as exc:
            report.add("fields", str(exc), part=part_name)
            return
        if target not in bookmark_names:
            report.add(
                "fields",
                f'REF field target bookmark "{target}" was not found',
                part=part_name,
            )
        return

    seq_match = _SEQ_INSTR_RE.match(normalized)
    if seq_match:
        try:
            FieldInstructionParser.validate_sequence_target(seq_match.group(1))
        except Exception as exc:
            report.add("fields", str(exc), part=part_name)
        return

    try:
        FieldInstructionParser.parse(normalized)
    except Exception as exc:
        report.add("fields", f"unsupported field instruction: {normalized!r} ({exc})", part=part_name)
