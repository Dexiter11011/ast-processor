"""Shared test constants and helpers."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

REQUIRED_PARTS = (
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
    "word/_rels/document.xml.rels",
    "word/styles.xml",
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def read_docx_part(docx_path: Path, part: str) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return zf.read(part)


def docx_namelist(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return zf.namelist()


def parse_document_xml(docx_path: Path) -> etree._Element:
    data = read_docx_part(docx_path, "word/document.xml")
    return etree.fromstring(data)
