"""In-memory representation of a DOCX template package."""

from __future__ import annotations

from dataclasses import dataclass, field

DOCUMENT_PART = "word/document.xml"
DOCUMENT_RELS_PART = "word/_rels/document.xml.rels"
CONTENT_TYPES_PART = "[Content_Types].xml"
STYLES_PART = "word/styles.xml"
NUMBERING_PART = "word/numbering.xml"
FOOTNOTES_PART = "word/footnotes.xml"

REQUIRED_TEMPLATE_PARTS = (
    CONTENT_TYPES_PART,
    "_rels/.rels",
    DOCUMENT_PART,
    DOCUMENT_RELS_PART,
    STYLES_PART,
)


@dataclass
class TemplatePackage:
    """Physical DOCX package parts keyed by ZIP entry path."""

    parts: dict[str, bytes] = field(default_factory=dict)

    def get_part(self, name: str) -> bytes:
        try:
            return self.parts[name]
        except KeyError as exc:
            raise KeyError(f"missing template part: {name}") from exc

    def has_part(self, name: str) -> bool:
        return name in self.parts

    def part_names(self) -> frozenset[str]:
        return frozenset(self.parts)

    def copy_parts(self) -> dict[str, bytes]:
        return dict(self.parts)
