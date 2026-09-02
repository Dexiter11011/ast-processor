"""Structured CLI diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostic:
    """Human-facing error diagnostic for CLI output."""

    message: str
    code: str | None = None
    path: str | None = None
    line: int | None = None
    column: int | None = None
    hint: str | None = None


def format_diagnostic(diagnostic: Diagnostic) -> str:
    """Format a diagnostic as a single-line or multi-line CLI message."""
    parts: list[str] = []
    if diagnostic.path and diagnostic.line is not None:
        location = f"{diagnostic.path}:{diagnostic.line}"
        if diagnostic.column is not None:
            location = f"{location}:{diagnostic.column}"
        parts.append(location)
    elif diagnostic.path:
        parts.append(diagnostic.path)
    parts.append(diagnostic.message)
    if diagnostic.hint:
        parts.append(diagnostic.hint)
    if len(parts) == 1:
        return parts[0]
    if diagnostic.path and diagnostic.line is not None:
        return f"{parts[0]}: {parts[1]}"
    if diagnostic.path and parts[0] == diagnostic.path:
        return f"{diagnostic.path}: {diagnostic.message}"
    return ": ".join(parts)
