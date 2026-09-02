"""Golden test for default word/styles.xml."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2docx.ooxml.styles import build_minimal_styles_xml
from tests.golden.xml_compare import assert_document_xml_equal


@pytest.fixture
def expected_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "expected"


def test_default_styles_xml_matches_golden(expected_dir: Path):
    expected_path = expected_dir / "default.styles.xml"
    assert expected_path.is_file(), "missing tests/expected/default.styles.xml"
    assert_document_xml_equal(expected_path.read_bytes(), build_minimal_styles_xml())


def test_styles_xml_defines_core_styles():
    from lxml import etree

    from tests.helpers import W_NS

    root = etree.fromstring(build_minimal_styles_xml())
    style_ids = {s.get(f"{{{W_NS}}}styleId") for s in root.findall(f"{{{W_NS}}}style")}
    assert {"Normal", "Heading1", "Heading2", "Heading3", "Quote", "NoSpacing", "Code", "Caption", "TOC1", "TOC2", "TOC3"}.issubset(style_ids)
