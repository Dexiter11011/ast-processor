"""Rich semantic document fragment."""

from __future__ import annotations

from dataclasses import dataclass

from md2docx.semantic.blocks import SemanticBlock


@dataclass(frozen=True)
class RichDocumentFragment:
    """Ordered semantic document content for plugin handlers and template regions."""

    blocks: tuple[SemanticBlock, ...] = ()

    def __add__(self, other: RichDocumentFragment) -> RichDocumentFragment:
        if not isinstance(other, RichDocumentFragment):
            return NotImplemented
        return RichDocumentFragment(self.blocks + other.blocks)

    def extend(self, *others: RichDocumentFragment) -> RichDocumentFragment:
        combined = self.blocks
        for item in others:
            combined += item.blocks
        return RichDocumentFragment(combined)

    @property
    def empty(self) -> bool:
        return not self.blocks
