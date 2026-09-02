"""Unit tests for structural XML comparison."""

from __future__ import annotations

import pytest
from lxml import etree

from tests.golden.xml_compare import assert_document_xml_equal, compare_elements


def _wrap(body: str) -> bytes:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    return xml.encode("utf-8")


def test_compare_elements_detects_text_mismatch():
    left = etree.fromstring(_wrap("<w:p><w:r><w:t>Hello</w:t></w:r></w:p>"))
    right = etree.fromstring(_wrap("<w:p><w:r><w:t>World</w:t></w:r></w:p>"))
    diffs = compare_elements(left, right)
    assert any("text" in line for line in diffs)


def test_assert_document_xml_equal_accepts_whitespace_only_text_difference():
    """None vs empty string text nodes are treated as equivalent."""
    left = _wrap("<w:p/>")
    right = _wrap("<w:p></w:p>")
    assert_document_xml_equal(left, right)


def test_assert_document_xml_equal_reports_attribute_diff():
    left = _wrap('<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr></w:p>')
    right = _wrap('<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr></w:p>')
    with pytest.raises(AssertionError, match="attributes differ"):
        assert_document_xml_equal(left, right)
