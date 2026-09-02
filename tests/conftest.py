"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import REQUIRED_PARTS, W_NS, docx_namelist, parse_document_xml, read_docx_part

__all__ = [
    "REQUIRED_PARTS",
    "W_NS",
    "docx_namelist",
    "fixtures_dir",
    "parse_document_xml",
    "read_docx_part",
]


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"
