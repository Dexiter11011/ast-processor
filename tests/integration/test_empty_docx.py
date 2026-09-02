"""End-to-end empty DOCX integration tests."""

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.cli.main import main
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import REQUIRED_PARTS, W_NS


def test_pipeline_empty_markdown(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "empty.md"
    output_path = tmp_path / "out.docx"
    convert_markdown_to_docx(input_path, output_path)

    assert output_path.is_file()
    with zipfile.ZipFile(output_path, "r") as zf:
        assert zf.testzip() is None
        for part in REQUIRED_PARTS:
            assert part in zf.namelist()


def test_cli_empty_markdown(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "empty.md"
    output_path = tmp_path / "cli-out.docx"
    code = main([str(input_path), "-o", str(output_path)])
    assert code == 0
    assert output_path.is_file()


def test_cli_auto_output_name(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "empty.md"
    output_path = tmp_path / "empty.docx"
    import shutil

    dest_input = tmp_path / "empty.md"
    shutil.copy(input_path, dest_input)
    code = main([str(dest_input)])
    assert code == 0
    assert output_path.is_file()


def test_cli_missing_input():
    code = main(["/nonexistent/file.md"])
    assert code == 1


def test_document_xml_valid_and_empty_body(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "out.docx"
    convert_markdown_to_docx(fixtures_dir / "empty.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    sect_pr = body.find(f"{{{W_NS}}}sectPr")
    assert sect_pr is not None
    pg_sz = sect_pr.find(f"{{{W_NS}}}pgSz")
    assert pg_sz is not None
    assert pg_sz.get(f"{{{W_NS}}}w") == "11906"
    assert pg_sz.get(f"{{{W_NS}}}h") == "16838"
    assert root.findall(f".//{{{W_NS}}}p") == []
