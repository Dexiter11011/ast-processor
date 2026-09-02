"""word/styles.xml generator with document, paragraph, and character styles."""

from __future__ import annotations

from md2docx.styles.theme import DefaultTheme
from md2docx.ooxml.styles_xml_writer import StylesXmlWriter


def build_minimal_styles_xml() -> bytes:
    """Build default word/styles.xml from the built-in theme."""
    theme = DefaultTheme.create()
    writer = StylesXmlWriter(document_defaults=theme.document_defaults)
    return writer.write(theme.build_registry())
