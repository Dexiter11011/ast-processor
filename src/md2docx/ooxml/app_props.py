"""docProps/app.xml builder."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import ns_tag, serialize, sub_element

_APP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"


def build_app_props_xml(*, application: str = "md2docx") -> bytes:
    root = etree.Element(ns_tag(_APP_NS, "Properties"), nsmap={None: _APP_NS})
    sub_element(root, "Application", text=application)
    sub_element(root, "DocSecurity", text="0")
    sub_element(root, "ScaleCrop", text="false")
    sub_element(root, "LinksUpToDate", text="false")
    sub_element(root, "SharedDoc", text="false")
    sub_element(root, "HyperlinksChanged", text="false")
    sub_element(root, "AppVersion", text="16.0000")
    return serialize(root)
