"""Semantic DOCX assertion helpers for contract tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.xml_builder import w_tag

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def read_document_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as archive:
        return archive.read("word/document.xml")


def read_styles_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as archive:
        return archive.read("word/styles.xml")


def paragraph_texts(document_xml: bytes) -> list[str]:
    root = etree.fromstring(document_xml)
    texts: list[str] = []
    for paragraph in root.findall(f".//{w_tag('body')}/{w_tag('p')}"):
        chunks = [(node.text or "") for node in paragraph.findall(f".//{w_tag('t')}")]
        texts.append("".join(chunks))
    return texts


def assert_contains_paragraph(document_xml: bytes, text: str) -> None:
    if text not in paragraph_texts(document_xml):
        joined = "\n".join(paragraph_texts(document_xml))
        raise AssertionError(f"paragraph {text!r} not found in:\n{joined}")


def assert_not_contains_paragraph(document_xml: bytes, text: str) -> None:
    if text in paragraph_texts(document_xml):
        raise AssertionError(f"paragraph {text!r} should not be present")


def assert_has_style(styles_xml: bytes, style_id: str) -> None:
    root = etree.fromstring(styles_xml)
    matches = root.xpath(
        f'.//*[local-name()="style"][@*[local-name()="styleId"]="{style_id}"]'
    )
    if not matches:
        raise AssertionError(f"style {style_id!r} not found in styles.xml")


def assert_has_bookmark(document_xml: bytes, name: str) -> None:
    root = etree.fromstring(document_xml)
    for node in root.iter(w_tag("bookmarkStart")):
        if node.get(w_tag("name")) == name:
            return
    raise AssertionError(f"bookmark {name!r} not found")


def assert_has_field(document_xml: bytes, instruction_fragment: str) -> None:
    root = etree.fromstring(document_xml)
    for node in root.iter(w_tag("instrText")):
        if instruction_fragment in (node.text or ""):
            return
    raise AssertionError(f"field instruction {instruction_fragment!r} not found")
