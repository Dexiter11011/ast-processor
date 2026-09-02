"""Embedded image/media parts for the DOCX package."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MediaManager:
    """Embedded image/media parts for the DOCX package."""

    parts: dict[str, bytes] = field(default_factory=dict)
    _counter: int = 0
    _doc_pr_id: int = 0

    def add_image(self, data: bytes, extension: str) -> str:
        self._counter += 1
        ext = extension.lower()
        if ext == "jpeg":
            ext = "jpg"
        media_name = f"image{self._counter}.{ext}"
        media_path = f"word/media/{media_name}"
        self.parts[media_path] = data
        return media_path

    def next_doc_pr_id(self) -> int:
        self._doc_pr_id += 1
        return self._doc_pr_id
