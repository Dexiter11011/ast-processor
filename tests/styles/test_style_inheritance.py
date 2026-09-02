"""Style inheritance serialization tests."""

from lxml import etree

from md2docx.styles.theme import DefaultTheme
from md2docx.ooxml.styles_xml_writer import StylesXmlWriter
from tests.helpers import W_NS


def test_heading_styles_based_on_normal():
    registry = DefaultTheme.create().build_registry()
    xml = StylesXmlWriter(document_defaults=DefaultTheme.create().document_defaults).write(registry)
    root = etree.fromstring(xml)

    heading1 = next(
        s for s in root.findall(f"{{{W_NS}}}style") if s.get(f"{{{W_NS}}}styleId") == "Heading1"
    )
    based_on = heading1.find(f"{{{W_NS}}}basedOn")
    assert based_on is not None
    assert based_on.get(f"{{{W_NS}}}val") == "Normal"
