"""DocxPackageWriter tests."""

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.document import OoxmlDocument
from md2docx.ooxml.package import DocxPackageWriter
from tests.helpers import REQUIRED_PARTS, W_NS


def test_write_empty_docx_produces_required_parts(tmp_path: Path):
    output = tmp_path / "empty.docx"
    DocxPackageWriter().write(OoxmlDocument(), output)

    assert output.is_file()
    assert zipfile.is_zipfile(output)

    with zipfile.ZipFile(output, "r") as zf:
        assert zf.testzip() is None
        names = set(zf.namelist())
        for part in REQUIRED_PARTS:
            assert part in names


def test_empty_body_has_only_sect_pr(tmp_path: Path):
    output = tmp_path / "empty.docx"
    DocxPackageWriter().write(OoxmlDocument(), output)

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    children = list(body)
    assert len(children) == 1
    assert children[0].tag == f"{{{W_NS}}}sectPr"

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert paragraphs == []
