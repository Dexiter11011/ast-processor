"""Metadata normalization tests."""

from __future__ import annotations

import pytest

from md2docx.metadata.errors import MetadataValidationError
from md2docx.metadata.normalize import normalize_date, normalize_keywords, normalize_optional_string


def test_normalize_optional_string():
    assert normalize_optional_string(None) is None
    assert normalize_optional_string("  hello  ") == "hello"
    assert normalize_optional_string("") is None
    assert normalize_optional_string("   ") is None


def test_normalize_date_iso():
    assert normalize_date("2026-08-31") == "2026-08-31"


def test_normalize_date_from_datetime():
    assert normalize_date("2026-08-31T12:30:00") == "2026-08-31"


def test_normalize_date_invalid():
    with pytest.raises(MetadataValidationError):
        normalize_date("31-08-2026")


def test_normalize_keywords():
    assert normalize_keywords("a, b, c") == ("a", "b", "c")
    assert normalize_keywords(None) == ()
    assert normalize_keywords("") == ()
