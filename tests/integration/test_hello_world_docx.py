"""End-to-end hello-world DOCX integration tests."""

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.cli.main import main
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def test_pipeline_hello_world(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "hello-world.docx"
    convert_markdown_to_docx(input_path, output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    paragraphs = root.findall(f".//{{{W_NS}}}p")
    assert len(paragraphs) == 1
    text_el = paragraphs[0].find(f".//{{{W_NS}}}t")
    assert text_el is not None
    assert text_el.text == "Hello world"


def test_cli_hello_world(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "hello-world.md"
    output_path = tmp_path / "hello-world.docx"
    code = main([str(input_path), "-o", str(output_path)])
    assert code == 0
    assert output_path.is_file()


def test_hello_world_structure_w_p_r_t(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "out.docx"
    convert_markdown_to_docx(fixtures_dir / "hello-world.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    p = body.find(f"{{{W_NS}}}p")
    assert p is not None
    r = p.find(f"{{{W_NS}}}r")
    assert r is not None
    t = r.find(f"{{{W_NS}}}t")
    assert t is not None
    assert t.text == "Hello world"
