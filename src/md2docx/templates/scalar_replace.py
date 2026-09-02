"""Replace scalar template placeholders while preserving paragraph formatting."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import w_tag
from md2docx.templates.errors import TemplatePlaceholderError
from md2docx.templates.placeholders import TemplatePlaceholder


def validate_scalar_value(name: str, value: str) -> None:
    if "\n" in value or "\r" in value:
        raise TemplatePlaceholderError(
            f'template placeholder "{{{{{name}}}}}" value must not contain newlines'
        )


def replace_scalar_placeholder(
    paragraph: etree._Element,
    placeholder: TemplatePlaceholder,
    value: str,
) -> None:
    """Replace a standalone scalar placeholder paragraph in place."""
    validate_scalar_value(placeholder.name, value)

    runs = [child for child in paragraph if etree.QName(child).localname == "r"]
    if not runs:
        run = etree.SubElement(paragraph, w_tag("r"))
        run.append(build_text(value))
        return

    first_run = runs[0]
    text_nodes = [node for node in first_run if etree.QName(node).localname == "t"]
    if text_nodes:
        text_nodes[0].text = value
        if value.startswith(" ") or value.endswith(" "):
            text_nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        else:
            text_nodes[0].attrib.pop("{http://www.w3.org/XML/1998/namespace}space", None)
        for extra in text_nodes[1:]:
            first_run.remove(extra)
    else:
        first_run.append(build_text(value))

    for extra_run in runs[1:]:
        paragraph.remove(extra_run)
