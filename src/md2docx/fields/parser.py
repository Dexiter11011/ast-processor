"""Parse and validate supported field instruction strings."""

from __future__ import annotations

import re

from md2docx.fields.errors import InvalidFieldTargetError, UnknownFieldInstructionError
from md2docx.fields.kinds import FieldKind
from md2docx.fields.model import DynamicField

_SIMPLE_KINDS = frozenset(
    {
        FieldKind.PAGE,
        FieldKind.NUMPAGES,
        FieldKind.DATE,
        FieldKind.AUTHOR,
        FieldKind.TITLE,
    }
)
_FORBIDDEN_TOKENS = ("EXEC", "MACRO", "INCLUDE", "IF", "COMPARE")
_BOOKMARK_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]{0,39}$")
_SEQUENCE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{0,39}$")


class FieldInstructionParser:
    """Parse whitelisted field instructions into DynamicField objects."""

    @staticmethod
    def parse(instruction: str) -> DynamicField:
        normalized = " ".join(instruction.strip().split())
        if not normalized:
            raise UnknownFieldInstructionError("empty field instruction")
        upper = normalized.upper()
        for token in _FORBIDDEN_TOKENS:
            if token in upper:
                raise UnknownFieldInstructionError(
                    f"unsupported field instruction token: {token}"
                )

        parts = normalized.split()
        keyword = parts[0].upper()
        try:
            kind = FieldKind(keyword)
        except ValueError as exc:
            raise UnknownFieldInstructionError(
                f"unknown field instruction: {keyword}"
            ) from exc

        if kind in _SIMPLE_KINDS:
            if len(parts) > 1:
                raise UnknownFieldInstructionError(
                    f"field instruction {keyword} does not accept parameters"
                )
            return DynamicField(kind=kind)

        if kind is FieldKind.REF:
            if len(parts) < 2:
                raise UnknownFieldInstructionError("REF field requires a bookmark name")
            target = parts[1]
            FieldInstructionParser.validate_bookmark_target(target)
            switches = tuple(part for part in parts[2:] if part.startswith("\\"))
            return DynamicField(kind=kind, target=target, switches=switches or ("\\h",))

        if kind is FieldKind.SEQ:
            if len(parts) < 2:
                raise UnknownFieldInstructionError("SEQ field requires a sequence name")
            target = " ".join(parts[1:])
            FieldInstructionParser.validate_sequence_target(target)
            switches = tuple(part for part in parts[2:] if part.startswith("\\"))
            return DynamicField(kind=kind, target=target, switches=switches)

        raise UnknownFieldInstructionError(f"unsupported field instruction: {keyword}")

    @staticmethod
    def validate_bookmark_target(name: str) -> None:
        if not _BOOKMARK_NAME_RE.match(name):
            raise InvalidFieldTargetError(f"invalid REF bookmark name: {name!r}")

    @staticmethod
    def validate_sequence_target(name: str) -> None:
        if not _SEQUENCE_NAME_RE.match(name):
            raise InvalidFieldTargetError(f"invalid SEQ sequence name: {name!r}")
