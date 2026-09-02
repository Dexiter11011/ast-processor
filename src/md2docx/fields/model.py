"""Dynamic field semantic model."""

from __future__ import annotations

from dataclasses import dataclass

from md2docx.fields.kinds import FieldKind


@dataclass(frozen=True)
class DynamicField:
    """Semantic representation of a supported dynamic Word field."""

    kind: FieldKind
    target: str | None = None
    switches: tuple[str, ...] = ()
