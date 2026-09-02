"""XML builder tests."""

from lxml import etree

from md2docx.ooxml.xml_builder import CT_NS, PKG_NS, element, serialize, sub_element, text_element, w_tag


def test_text_element_escapes_special_characters():
    el = text_element("t", 'A & B <tag> "quote" \'apos\'')
    xml = serialize(el).decode("utf-8")
    assert "&amp;" in xml
    assert "&lt;" in xml
    assert "&gt;" in xml
    assert "A & B" not in xml
    assert "<tag>" not in xml
    parsed = etree.fromstring(serialize(el))
    assert parsed.text == 'A & B <tag> "quote" \'apos\''


def test_roundtrip_parse():
    el = text_element("t", "Hello")
    parsed = etree.fromstring(serialize(el))
    assert parsed.tag == w_tag("t")
    assert parsed.text == "Hello"


def test_element_with_attrs_and_children():
    rel = element(
        "Relationship",
        ns=PKG_NS,
        nsmap={None: PKG_NS},
        attrs={"Id": "rId1", "Target": "https://example.com?q=a&b=1"},
    )
    xml = serialize(rel).decode("utf-8")
    assert 'Target="https://example.com?q=a&amp;b=1"' in xml


def test_sub_element_inherits_parent_namespace():
    root = etree.Element(f"{{{CT_NS}}}Types", nsmap={None: CT_NS})
    child = sub_element(root, "Default", attrs={"Extension": "xml", "ContentType": "application/xml"})
    assert child.tag == f"{{{CT_NS}}}Default"
