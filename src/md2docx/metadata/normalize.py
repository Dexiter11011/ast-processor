"""Normalize metadata values from CLI and front matter."""

from __future__ import annotations

import re
from datetime import datetime

from md2docx.metadata.errors import MetadataValidationError

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?$"
)

_CONFIG_KEYS = frozenset({"theme", "template"})


def normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalize_date(value: str | None, *, field: str = "date") -> str | None:
    """Normalize to canonical ISO date string YYYY-MM-DD."""
    normalized = normalize_optional_string(value)
    if normalized is None:
        return None
    if _ISO_DATE_RE.match(normalized):
        return normalized
    if _ISO_DATETIME_RE.match(normalized):
        try:
            if normalized.endswith("Z"):
                parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
            else:
                parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise MetadataValidationError(
                f'invalid {field} value: "{value}"',
                field=field,
            ) from exc
        return parsed.date().isoformat()
    raise MetadataValidationError(
        f'invalid {field} value: "{value}" (expected YYYY-MM-DD)',
        field=field,
    )


def normalize_keywords(value: str | None) -> tuple[str, ...]:
    """Parse comma-separated or plain string keywords into a normalized tuple."""
    normalized = normalize_optional_string(value)
    if normalized is None:
        return ()
    parts = [part.strip() for part in normalized.split(",")]
    return tuple(part for part in parts if part)


def normalize_keywords_list(items: list[str]) -> tuple[str, ...]:
    return tuple(part.strip() for item in items for part in [item] if part.strip())


def is_config_key(key: str) -> bool:
    return key.strip().lower() in _CONFIG_KEYS
