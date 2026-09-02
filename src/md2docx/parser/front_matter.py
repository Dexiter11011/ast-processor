"""Parse optional YAML-like front matter from Markdown sources."""

from __future__ import annotations

import re

from md2docx.ast.metadata import DocumentMetadata
from md2docx.metadata.normalize import is_config_key, normalize_keywords

_FRONT_MATTER_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
_KNOWN_KEYS = {"title", "author", "subject", "keywords", "date"}


def split_front_matter(source: str) -> tuple[dict[str, str], str]:
    match = _FRONT_MATTER_RE.match(source)
    if match is None:
        return {}, source
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        normalized = key.strip().lower()
        if is_config_key(normalized):
            continue
        if normalized in _KNOWN_KEYS:
            metadata[normalized] = value.strip()
    return metadata, source[match.end() :]


def parse_document_metadata(raw: dict[str, str]) -> DocumentMetadata:
    keywords = normalize_keywords(raw.get("keywords"))
    return DocumentMetadata(
        title=raw.get("title", ""),
        author=raw.get("author", ""),
        subject=raw.get("subject", ""),
        keywords=", ".join(keywords) if keywords else "",
        date=raw.get("date", ""),
    )
