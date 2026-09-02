"""Bookmark integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _bookmark_names(root: etree._Element) -> list[str]:
    return [
        el.get(f"{{{W_NS}}}name")
        for el in root.findall(f".//{{{W_NS}}}bookmarkStart")
    ]


def _bookmark_ids(root: etree._Element) -> list[str]:
    return [
        el.get(f"{{{W_NS}}}id")
        for el in root.findall(f".//{{{W_NS}}}bookmarkStart")
    ]


def test_heading_bookmark(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "bookmarks.docx"
    convert_markdown_to_docx(fixtures_dir / "bookmarks.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    assert _bookmark_names(root) == ["hello-world"]
    assert len(set(_bookmark_ids(root))) == 1


def test_duplicate_heading_bookmarks(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "duplicate.docx"
    convert_markdown_to_docx(fixtures_dir / "duplicate-heading-bookmarks.md", output)
    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    assert _bookmark_names(root) == ["introduction", "introduction-1", "introduction-2"]
    assert len(_bookmark_ids(root)) == len(set(_bookmark_ids(root)))
