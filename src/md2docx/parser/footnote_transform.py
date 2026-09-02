"""Validate footnote references and definitions after parsing."""

from __future__ import annotations

import re

from md2docx.ast.types import Document, FootnoteDefinition, FootnoteReference
from md2docx.parser.errors import FootnoteParseError

_FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)


def _collect_footnote_refs(nodes) -> list[str]:
    labels: list[str] = []
    for node in nodes:
        if isinstance(node, FootnoteReference):
            labels.append(node.label)
        children = getattr(node, "children", None)
        if children:
            labels.extend(_collect_footnote_refs(children))
        if hasattr(node, "items"):
            for item in node.items:
                labels.extend(_collect_footnote_refs(getattr(item, "term", [])))
                labels.extend(_collect_footnote_refs(getattr(item, "description", [])))
        if hasattr(node, "rows"):
            for row in node.rows:
                for cell in row.cells:
                    labels.extend(_collect_footnote_refs(cell.children))
    return labels


def apply_footnote_transform(
    document: Document,
    *,
    source_path: str | None = None,
    source: str | None = None,
) -> Document:
    """Validate footnote labels; unused definitions are allowed."""
    if source:
        counts: dict[str, int] = {}
        for match in _FOOTNOTE_DEF_RE.finditer(source):
            label = match.group(1)
            counts[label] = counts.get(label, 0) + 1
            if counts[label] > 1:
                raise FootnoteParseError(
                    f"duplicate footnote definition: {label}",
                    path=source_path,
                )

    definitions: dict[str, FootnoteDefinition] = {}
    for definition in document.footnotes:
        if not definition.children:
            raise FootnoteParseError(
                f"undefined footnote: {definition.label}",
                path=source_path,
            )
        if definition.label in definitions:
            raise FootnoteParseError(
                f"duplicate footnote definition: {definition.label}",
                path=source_path,
            )
        definitions[definition.label] = definition

    for label in _collect_footnote_refs(document.children):
        if label not in definitions:
            raise FootnoteParseError(
                f"undefined footnote: {label}",
                path=source_path,
            )

    return document
