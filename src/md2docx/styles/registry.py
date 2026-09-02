"""Style registry — one semantic style maps to one immutable definition."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.styles.definition import StyleDefinition


class DuplicateStyleError(ValueError):
    """Raised when registering a semantic style id twice."""


@dataclass
class StyleRegistry:
    """Registry of document styles keyed by semantic id."""

    _definitions: dict[str, StyleDefinition] = field(default_factory=dict)

    def register(self, definition: StyleDefinition) -> None:
        if definition.semantic_id in self._definitions:
            raise DuplicateStyleError(
                f"style already registered: {definition.semantic_id!r}"
            )
        self._definitions[definition.semantic_id] = definition

    def get(self, semantic_id: str) -> StyleDefinition:
        try:
            return self._definitions[semantic_id]
        except KeyError as exc:
            raise KeyError(f"unknown style: {semantic_id!r}") from exc

    def has(self, semantic_id: str) -> bool:
        return semantic_id in self._definitions

    def all_definitions(self) -> tuple[StyleDefinition, ...]:
        return tuple(self._definitions.values())

    def ooxml_id(self, semantic_id: str) -> str:
        return self.get(semantic_id).ooxml_id
