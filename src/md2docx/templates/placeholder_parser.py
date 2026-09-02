"""Parse standalone template placeholders from paragraph text."""

from __future__ import annotations

import re

from md2docx.templates.errors import TemplatePlaceholderError

_PLACEHOLDER_RE = re.compile(r"^\{\{\s*([a-z][a-z0-9_]*)\s*\}\}$")
_BRACE_FRAGMENT_RE = re.compile(r"\{\{|\}\}")


class TemplatePlaceholderParser:
    """Recognize strict standalone ``{{name}}`` placeholders."""

    @staticmethod
    def normalize_name(raw: str) -> str:
        """Return normalized placeholder name from a standalone token."""
        match = _PLACEHOLDER_RE.match(raw.strip())
        if match is None:
            raise TemplatePlaceholderError(
                f'invalid template placeholder syntax: "{raw.strip()}"'
            )
        return match.group(1)

    @staticmethod
    def parse_standalone(paragraph_text: str) -> str | None:
        """Return normalized name when the paragraph is exactly one placeholder."""
        stripped = paragraph_text.strip()
        if not stripped:
            return None
        if not _BRACE_FRAGMENT_RE.search(stripped):
            return None
        if not _PLACEHOLDER_RE.match(stripped):
            if "{{" in stripped or "}}" in stripped:
                raise TemplatePlaceholderError(
                    "inline template placeholders are not supported"
                )
            return None
        return TemplatePlaceholderParser.normalize_name(stripped)

    @staticmethod
    def looks_like_placeholder_paragraph(paragraph_text: str) -> bool:
        stripped = paragraph_text.strip()
        return "{{" in stripped or "}}" in stripped
