#!/usr/bin/env python3
"""Build DOCX template fixtures for tests and examples."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.bookmark import build_bookmark_end, build_bookmark_start
from md2docx.ooxml import api
from md2docx.ooxml.content_types import build_content_types_xml
from md2docx.ooxml.header_footer import build_footer_part, build_header_part
from md2docx.ooxml.relationships import (
    FOOTER_REL_TYPE,
    HEADER_REL_TYPE,
    RelationshipManager,
    STYLES_REL_TYPE,
)
from md2docx.ooxml.styles import build_minimal_styles_xml
from md2docx.ooxml.xml_builder import R_NS, W_NS, serialize, w_attr, w_tag
from md2docx.templates.insertion import CONTENT_PLACEHOLDER

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "templates"
EXAMPLES_DIR = ROOT / "examples" / "templates"


def _paragraph(text: str, *, style_id: str = "Normal") -> bytes:
    element = api.paragraph([api.run(text)], style_id=style_id)
    return element


def _default_sect_pr(*, header_rel_id: str | None = None, footer_rel_id: str | None = None) -> etree._Element:
    sect_pr = etree.Element(w_tag("sectPr"), nsmap={"w": W_NS, "r": R_NS})
    pg_sz = etree.SubElement(sect_pr, w_tag("pgSz"))
    pg_sz.set(w_attr("w"), "11906")
    pg_sz.set(w_attr("h"), "16838")
    if header_rel_id:
        header_ref = etree.SubElement(sect_pr, w_tag("headerReference"))
        header_ref.set(w_attr("type"), "default")
        header_ref.set(f"{{{R_NS}}}id", header_rel_id)
    if footer_rel_id:
        footer_ref = etree.SubElement(sect_pr, w_tag("footerReference"))
        footer_ref.set(w_attr("type"), "default")
        footer_ref.set(f"{{{R_NS}}}id", footer_rel_id)
    return sect_pr


def _build_document_xml(paragraphs: list[etree._Element], *, sect_pr: etree._Element | None = None) -> bytes:
    body = etree.Element(w_tag("body"), nsmap={"w": W_NS})
    for paragraph in paragraphs:
        body.append(paragraph)
    body.append(sect_pr or _default_sect_pr())
    root = etree.Element(w_tag("document"), nsmap={"w": W_NS, "r": R_NS})
    root.append(body)
    return serialize(root)


def _write_docx(path: Path, parts: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(parts):
            zf.writestr(name, parts[name])
    path.write_bytes(buf.getvalue())


def build_minimal_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    styles_xml = build_minimal_styles_xml()
    paragraphs = [
        api.paragraph([api.run("Introduction")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
        api.paragraph([api.run("Signature")], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": styles_xml,
    }
    return parts


def build_placeholders_basic_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    styles_xml = build_minimal_styles_xml()
    paragraphs = [
        api.paragraph([api.run("Title:")], style_id="Normal"),
        api.paragraph([api.run("{{title}}")], style_id="Normal"),
        api.paragraph([api.run("Author:")], style_id="Normal"),
        api.paragraph([api.run("{{author}}")], style_id="Normal"),
        api.paragraph([api.run("Date:")], style_id="Normal"),
        api.paragraph([api.run("{{date}}")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": styles_xml,
    }
    return parts


def build_placeholders_formatting_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    styles_xml = build_minimal_styles_xml()
    paragraphs = [
        api.paragraph([api.run("Heading 1:")], style_id="Normal"),
        api.paragraph([api.run("{{title}}")], style_id="Heading1"),
        api.paragraph([api.run("Author paragraph:")], style_id="Normal"),
        api.paragraph([api.run("{{author}}")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": styles_xml,
    }
    return parts


def _paragraph_with_bookmark(text: str, name: str, bookmark_id: int, *, style_id: str = "Normal") -> etree._Element:
    para = api.paragraph([api.run(text)], style_id=style_id)
    para.insert(0, build_bookmark_start(name, bookmark_id))
    para.append(build_bookmark_end(bookmark_id))
    return para


def build_corporate_navigation_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    header_rel = rels.add(HEADER_REL_TYPE, "header1.xml")
    footer_rel = rels.add(FOOTER_REL_TYPE, "footer1.xml")

    header_xml = build_header_part(
        [api.paragraph([api.run("Company Name")], style_id="Normal")]
    )
    footer_xml = build_footer_part(
        [api.paragraph([api.run("Confidential")], style_id="Normal")]
    )

    paragraphs = [
        api.paragraph([api.run("Table of Contents")], style_id="Normal"),
        api.toc_field(min_level=1, max_level=3),
        api.paragraph([api.run("List of Figures")], style_id="Normal"),
        api.lof_field(),
        api.paragraph([api.run("List of Tables")], style_id="Normal"),
        api.lot_field(),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    sect_pr = _default_sect_pr(header_rel_id=header_rel, footer_rel_id=footer_rel)
    document_xml = _build_document_xml(paragraphs, sect_pr=sect_pr)
    header_path = "word/header1.xml"
    footer_path = "word/footer1.xml"
    parts = {
        "[Content_Types].xml": build_content_types_xml(
            header_parts=[header_path],
            footer_parts=[footer_path],
        ),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
        header_path: header_xml,
        footer_path: footer_xml,
    }
    return parts


def build_navigation_collision_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    paragraphs = [
        _paragraph_with_bookmark("Template Architecture", "architecture", 0),
        _paragraph_with_bookmark("Template Figure", "figure-architecture", 1),
        _paragraph_with_bookmark("Template Table", "table-results", 2),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    return parts


def build_regions_basic_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    paragraphs = [
        api.paragraph([api.run("Table of Contents")], style_id="Normal"),
        api.paragraph([api.run("{{toc}}")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    return parts


def build_regions_navigation_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    paragraphs = [
        api.paragraph([api.run("Table of Contents")], style_id="Normal"),
        api.paragraph([api.run("{{toc}}")], style_id="Normal"),
        api.paragraph([api.run("List of Figures")], style_id="Normal"),
        api.paragraph([api.run("{{list_of_figures}}")], style_id="Normal"),
        api.paragraph([api.run("List of Tables")], style_id="Normal"),
        api.paragraph([api.run("{{list_of_tables}}")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    return parts


def build_regions_complex_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    paragraphs = [
        api.paragraph([api.run("Title:")], style_id="Normal"),
        api.paragraph([api.run("{{title}}")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
        api.paragraph([api.run("Appendix navigation")], style_id="Normal"),
        api.paragraph([api.run("{{toc}}")], style_id="Normal"),
        api.paragraph([api.run("{{list_of_figures}}")], style_id="Normal"),
    ]
    document_xml = _build_document_xml(paragraphs)
    parts = {
        "[Content_Types].xml": build_content_types_xml(),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
    }
    return parts


def build_corporate_template() -> dict[str, bytes]:
    rels = RelationshipManager()
    rels.add_styles_relationship()
    header_rel = rels.add(HEADER_REL_TYPE, "header1.xml")
    footer_rel = rels.add(FOOTER_REL_TYPE, "footer1.xml")

    header_xml = build_header_part(
        [api.paragraph([api.run("Company Name")], style_id="Normal")]
    )
    footer_xml = build_footer_part(
        [api.paragraph([api.run("Confidential")], style_id="Normal")]
    )

    paragraphs = [
        api.paragraph([api.run("Introduction")], style_id="Normal"),
        api.paragraph([api.run(CONTENT_PLACEHOLDER)], style_id="Normal"),
        api.paragraph([api.run("Signature")], style_id="Normal"),
    ]
    sect_pr = _default_sect_pr(header_rel_id=header_rel, footer_rel_id=footer_rel)
    document_xml = _build_document_xml(paragraphs, sect_pr=sect_pr)
    header_path = "word/header1.xml"
    footer_path = "word/footer1.xml"
    parts = {
        "[Content_Types].xml": build_content_types_xml(
            header_parts=[header_path],
            footer_parts=[footer_path],
        ),
        "_rels/.rels": rels.build_root_rels_xml(include_doc_props=False),
        "word/document.xml": document_xml,
        "word/_rels/document.xml.rels": rels.build_document_rels_xml(),
        "word/styles.xml": build_minimal_styles_xml(),
        header_path: header_xml,
        footer_path: footer_xml,
    }
    return parts


def main() -> None:
    targets = {
        FIXTURES_DIR / "minimal.docx": build_minimal_template(),
        FIXTURES_DIR / "corporate.docx": build_corporate_template(),
        FIXTURES_DIR / "corporate-navigation.docx": build_corporate_navigation_template(),
        FIXTURES_DIR / "navigation-collision.docx": build_navigation_collision_template(),
        FIXTURES_DIR / "placeholders-basic.docx": build_placeholders_basic_template(),
        FIXTURES_DIR / "placeholders-formatting.docx": build_placeholders_formatting_template(),
        FIXTURES_DIR / "regions-basic.docx": build_regions_basic_template(),
        FIXTURES_DIR / "regions-navigation.docx": build_regions_navigation_template(),
        FIXTURES_DIR / "regions-complex.docx": build_regions_complex_template(),
        EXAMPLES_DIR / "corporate.docx": build_corporate_template(),
        EXAMPLES_DIR / "placeholders.docx": build_placeholders_basic_template(),
    }
    for path, parts in targets.items():
        _write_docx(path, parts)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
