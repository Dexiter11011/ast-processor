"""Safe XML element building and serialization via lxml.

All OOXML parts must be built through this module (or helpers that delegate
here). Do not concatenate XML tag strings with user content — lxml escapes
text nodes and attribute values during serialization.
"""

from __future__ import annotations

from typing import Union
from xml.sax.saxutils import escape

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
XML_NS = "http://www.w3.org/XML/1998/namespace"

NSMAP = {"w": W_NS}

XmlChild = Union[etree._Element, str]
XmlAttrs = dict[str, str]


def xml_escape(value: str) -> str:
    """Escape text for XML attribute values when manual escaping is unavoidable."""
    return escape(value, {"'": "&apos;", '"': "&quot;"})


def w_tag(local: str) -> str:
    return f"{{{W_NS}}}{local}"


def w_attr(local: str) -> str:
    return f"{{{W_NS}}}{local}"


def ns_tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}"


def w_element(local: str) -> etree._Element:
    """Create a namespaced WordprocessingML element with the default w: prefix."""
    return etree.Element(w_tag(local), nsmap=NSMAP)


def element(
    local: str,
    *,
    ns: str = W_NS,
    nsmap: dict[str, str] | None = None,
    attrs: XmlAttrs | None = None,
    text: str | None = None,
    children: list[XmlChild] | None = None,
) -> etree._Element:
    """Create an XML element with optional attributes, text, and child nodes."""
    qname = ns_tag(ns, local)
    el = etree.Element(qname, nsmap=nsmap) if nsmap else etree.Element(qname)
    if attrs:
        for key, value in attrs.items():
            _set_attr(el, key, value)
    if text is not None:
        el.text = text
    if children:
        for child in children:
            if isinstance(child, str):
                if el.text is None and len(el) == 0:
                    el.text = child
                else:
                    if len(el) == 0:
                        el.text = el.text or ""
                    tail_el = el if len(el) == 0 else el[-1]
                    tail_el.tail = (tail_el.tail or "") + child
            else:
                el.append(child)
    return el


def sub_element(
    parent: etree._Element,
    local: str,
    *,
    ns: str | None = None,
    attrs: XmlAttrs | None = None,
    text: str | None = None,
) -> etree._Element:
    """Append a namespaced child element; infer namespace from parent when omitted."""
    if ns is None:
        if parent.tag.startswith("{"):
            ns = parent.tag[1 : parent.tag.index("}")]
        else:
            ns = W_NS
    child = etree.SubElement(parent, ns_tag(ns, local))
    if attrs:
        for key, value in attrs.items():
            _set_attr(child, key, value)
    if text is not None:
        child.text = text
    return child


def text_element(
    local: str,
    value: str,
    *,
    ns: str = W_NS,
    nsmap: dict[str, str] | None = None,
    attrs: XmlAttrs | None = None,
) -> etree._Element:
    """Create an element whose text content is escaped by the serializer."""
    return element(local, ns=ns, nsmap=nsmap, attrs=attrs, text=value)


def serialize(element: etree._Element) -> bytes:
    """Serialize an element tree to UTF-8 XML with declaration."""
    return etree.tostring(element, xml_declaration=True, encoding="UTF-8", standalone=True)


def _set_attr(el: etree._Element, key: str, value: str) -> None:
    if key.startswith("{"):
        el.set(key, value)
        return
    if ":" in key:
        prefix, local = key.split(":", 1)
        if prefix == "w":
            el.set(w_attr(local), value)
        elif prefix == "r":
            el.set(f"{{{R_NS}}}{local}", value)
        elif prefix == "xml":
            el.set(f"{{{XML_NS}}}{local}", value)
        else:
            el.set(key, value)
    else:
        el.set(key, value)
