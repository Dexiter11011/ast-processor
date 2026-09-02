"""Generate word/styles.xml from StyleRegistry definitions."""

from __future__ import annotations

from lxml import etree

from md2docx.styles.definition import DocumentDefaults, ParagraphStyle, RunStyle, StyleDefinition
from md2docx.styles.registry import StyleRegistry
from md2docx.ooxml.xml_builder import W_NS, serialize, w_attr, w_tag


class StylesXmlWriter:
    """Serialize StyleDefinition objects to word/styles.xml."""

    def __init__(self, *, document_defaults: DocumentDefaults | None = None) -> None:
        self._document_defaults = document_defaults or DocumentDefaults()

    def write(self, registry: StyleRegistry) -> bytes:
        root = etree.Element(w_tag("styles"), nsmap={"w": W_NS})
        self._append_doc_defaults(root)
        for definition in registry.all_definitions():
            if definition.style_type == "paragraph":
                root.append(self._paragraph_style(definition, registry))
            elif definition.style_type == "table":
                root.append(self._table_style(definition))
            else:
                root.append(self._character_style(definition))
        return serialize(root)

    def _append_doc_defaults(self, root: etree._Element) -> None:
        defaults = self._document_defaults
        doc_defaults = etree.SubElement(root, w_tag("docDefaults"))
        r_pr_default = etree.SubElement(doc_defaults, w_tag("rPrDefault"))
        r_pr = etree.SubElement(r_pr_default, w_tag("rPr"))
        self._append_fonts(r_pr, defaults.font_family)
        sz = etree.SubElement(r_pr, w_tag("sz"))
        sz.set(w_attr("val"), str(defaults.font_size))
        sz_cs = etree.SubElement(r_pr, w_tag("szCs"))
        sz_cs.set(w_attr("val"), str(defaults.font_size))

    def _style_base(self, definition: StyleDefinition, registry: StyleRegistry) -> etree._Element:
        style = etree.Element(w_tag("style"), nsmap={"w": W_NS})
        style.set(w_attr("type"), definition.style_type)
        style.set(w_attr("styleId"), definition.ooxml_id)
        if definition.ui_priority is not None:
            style.set(w_attr("uiPriority"), str(definition.ui_priority))
        if definition.q_format:
            style.set(w_attr("qFormat"), "1")
        name_el = etree.SubElement(style, w_tag("name"))
        name_el.set(w_attr("val"), definition.name)
        if definition.based_on is not None:
            based = etree.SubElement(style, w_tag("basedOn"))
            based.set(w_attr("val"), registry.ooxml_id(definition.based_on))
        if definition.next_style is not None:
            nxt = etree.SubElement(style, w_tag("next"))
            nxt.set(w_attr("val"), registry.ooxml_id(definition.next_style))
        return style

    def _paragraph_style(self, definition: StyleDefinition, registry: StyleRegistry) -> etree._Element:
        style = self._style_base(definition, registry)
        p_pr = etree.SubElement(style, w_tag("pPr"))
        if definition.paragraph is not None:
            self._append_paragraph_props(p_pr, definition.paragraph)
        else:
            self._append_default_paragraph_spacing(p_pr)
        if definition.run is not None:
            r_pr = etree.SubElement(style, w_tag("rPr"))
            self._append_run_props(r_pr, definition.run)
        return style

    def _character_style(self, definition: StyleDefinition) -> etree._Element:
        style = etree.Element(w_tag("style"), nsmap={"w": W_NS})
        style.set(w_attr("type"), "character")
        style.set(w_attr("styleId"), definition.ooxml_id)
        if definition.ui_priority is not None:
            style.set(w_attr("uiPriority"), str(definition.ui_priority))
        name_el = etree.SubElement(style, w_tag("name"))
        name_el.set(w_attr("val"), definition.name)
        if definition.run is not None:
            r_pr = etree.SubElement(style, w_tag("rPr"))
            self._append_run_props(r_pr, definition.run)
        return style

    def _table_style(self, definition: StyleDefinition) -> etree._Element:
        style = etree.Element(w_tag("style"), nsmap={"w": W_NS})
        style.set(w_attr("type"), "table")
        style.set(w_attr("styleId"), definition.ooxml_id)
        if definition.ui_priority is not None:
            style.set(w_attr("uiPriority"), str(definition.ui_priority))
        if definition.q_format:
            style.set(w_attr("qFormat"), "1")
        name_el = etree.SubElement(style, w_tag("name"))
        name_el.set(w_attr("val"), definition.name)
        return style

    def _append_default_paragraph_spacing(self, p_pr: etree._Element) -> None:
        spacing = etree.SubElement(p_pr, w_tag("spacing"))
        spacing.set(w_attr("after"), "160")
        spacing.set(w_attr("line"), "259")
        spacing.set(w_attr("lineRule"), "auto")

    def _append_paragraph_props(self, p_pr: etree._Element, paragraph: ParagraphStyle) -> None:
        if (
            paragraph.spacing_before is not None
            or paragraph.spacing_after is not None
            or paragraph.line_spacing is not None
        ):
            spacing = etree.SubElement(p_pr, w_tag("spacing"))
            if paragraph.spacing_before is not None:
                spacing.set(w_attr("before"), str(paragraph.spacing_before))
            if paragraph.spacing_after is not None:
                spacing.set(w_attr("after"), str(paragraph.spacing_after))
            if paragraph.line_spacing is not None:
                spacing.set(w_attr("line"), str(paragraph.line_spacing))
            if paragraph.line_rule is not None:
                spacing.set(w_attr("lineRule"), paragraph.line_rule)
        if paragraph.indent_left is not None:
            ind = etree.SubElement(p_pr, w_tag("ind"))
            ind.set(w_attr("left"), str(paragraph.indent_left))
        if paragraph.contextual_spacing:
            etree.SubElement(p_pr, w_tag("contextualSpacing"))

    def _append_run_props(self, r_pr: etree._Element, run: RunStyle) -> None:
        if run.font_family is not None:
            self._append_fonts(r_pr, run.font_family)
        if run.bold:
            etree.SubElement(r_pr, w_tag("b"))
        if run.italic:
            etree.SubElement(r_pr, w_tag("i"))
            etree.SubElement(r_pr, w_tag("iCs"))
        if run.font_size is not None:
            sz = etree.SubElement(r_pr, w_tag("sz"))
            sz.set(w_attr("val"), str(run.font_size))
            sz_cs = etree.SubElement(r_pr, w_tag("szCs"))
            sz_cs.set(w_attr("val"), str(run.font_size))
        if run.color is not None:
            color = etree.SubElement(r_pr, w_tag("color"))
            color.set(w_attr("val"), run.color)

    def _append_fonts(self, r_pr: etree._Element, font_family: str) -> None:
        fonts = etree.SubElement(r_pr, w_tag("rFonts"))
        fonts.set(w_attr("ascii"), font_family)
        fonts.set(w_attr("hAnsi"), font_family)
        if font_family == "Calibri":
            fonts.set(w_attr("eastAsia"), font_family)
        fonts.set(w_attr("cs"), font_family)
