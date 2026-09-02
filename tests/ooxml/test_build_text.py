"""OOXML text builder tests."""

from lxml import etree

from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import serialize, xml_escape


def test_xml_escape():
    assert xml_escape('A & B <tag> "quote" \'apos\'') == (
        "A &amp; B &lt;tag&gt; &quot;quote&quot; &apos;apos&apos;"
    )


def test_build_text_escapes_special_characters():
    el = build_text('A & B <tag> "quote" \'apos\'')
    xml = serialize(el).decode("utf-8")
    assert "&amp;" in xml
    assert "&lt;" in xml
    assert "&gt;" in xml
    parsed = etree.fromstring(serialize(el))
    assert parsed.text == 'A & B <tag> "quote" \'apos\''


def test_build_text_preserves_leading_trailing_space():
    el = build_text(" spaced ")
    assert el.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"
    assert el.text == " spaced "
