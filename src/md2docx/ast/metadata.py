"""Document metadata carried from Markdown front matter to DOCX."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocumentMetadata:
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    date: str = ""

    def has_values(self) -> bool:
        return bool(self.title or self.author or self.subject or self.keywords)
