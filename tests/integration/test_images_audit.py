"""Image embedding audit — PNG, JPEG, dual images, missing file error."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.processor.errors import ImageNotFoundError
from md2docx.validation import validate_docx
from tests.helpers import R_NS, W_NS


def test_png_image_fixture(fixtures_dir: Path, tmp_path: Path):
    output = tmp_path / "png.docx"
    convert_markdown_to_docx(fixtures_dir / "image.md", output)
    assert validate_docx(output).ok


def test_jpeg_image_fixture(fixtures_dir: Path, tmp_path: Path):
    output = tmp_path / "jpeg.docx"
    convert_markdown_to_docx(fixtures_dir / "image-jpeg.md", output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()
    with zipfile.ZipFile(output, "r") as zf:
        assert any(n.endswith(".jpg") for n in zf.namelist())


def test_dual_images_have_two_media_parts(fixtures_dir: Path, tmp_path: Path):
    output = tmp_path / "dual.docx"
    convert_markdown_to_docx(fixtures_dir / "images-dual.md", output)
    assert validate_docx(output).ok
    with zipfile.ZipFile(output, "r") as zf:
        media = [n for n in zf.namelist() if n.startswith("word/media/")]
        assert len(media) == 2
        root = __import__("lxml.etree", fromlist=["etree"]).fromstring(zf.read("word/document.xml"))
        embeds = {el.get(f"{{{R_NS}}}embed") for el in root.iter() if el.get(f"{{{R_NS}}}embed")}
        assert len(embeds) == 2


def test_missing_image_raises(tmp_path: Path, fixtures_dir: Path):
    with pytest.raises(ImageNotFoundError, match="image not found"):
        convert_markdown_to_docx(fixtures_dir / "malformed/missing-image.md", tmp_path / "x.docx")
