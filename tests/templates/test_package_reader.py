"""DocxPackageReader and TemplatePackage tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md2docx.ooxml.package import DocxPackageWriter
from md2docx.templates.errors import TemplateLoadError
from md2docx.templates.reader import DocxPackageReader
from md2docx.validation import validate_docx


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "templates"


def test_load_valid_minimal_template(templates_dir: Path):
    template = DocxPackageReader.load(templates_dir / "minimal.docx")
    assert template.has_part("word/document.xml")
    assert template.has_part("word/styles.xml")


def test_missing_template_file(tmp_path: Path):
    missing = tmp_path / "missing.docx"
    with pytest.raises(TemplateLoadError, match="template file not found"):
        DocxPackageReader.load(missing)


def test_invalid_zip_template(tmp_path: Path):
    broken = tmp_path / "broken.docx"
    broken.write_bytes(b"not-a-zip")
    with pytest.raises(TemplateLoadError, match="not a ZIP archive"):
        DocxPackageReader.load(broken)


def test_rejects_zip_slip_path(tmp_path: Path, templates_dir: Path):
    source = templates_dir / "minimal.docx"
    unsafe = tmp_path / "unsafe.docx"
    with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(unsafe, "w") as zout:
        for name in zin.namelist():
            zout.writestr(name, zin.read(name))
        zout.writestr("../evil.xml", b"<x/>")
    with pytest.raises(TemplateLoadError, match="invalid template entry path"):
        DocxPackageReader.load(unsafe)


def test_roundtrip_preserves_parts(tmp_path: Path, templates_dir: Path):
    source = DocxPackageReader.load(templates_dir / "corporate.docx")
    output = tmp_path / "roundtrip.docx"
    DocxPackageWriter().write_package(source.copy_parts(), output)
    roundtrip = DocxPackageReader.load(output)
    assert roundtrip.part_names() == source.part_names()
    for name in source.part_names():
        assert roundtrip.get_part(name) == source.get_part(name)


def test_roundtrip_output_is_valid_docx(tmp_path: Path, templates_dir: Path):
    source = DocxPackageReader.load(templates_dir / "corporate.docx")
    output = tmp_path / "roundtrip.docx"
    DocxPackageWriter().write_package(source.copy_parts(), output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()
