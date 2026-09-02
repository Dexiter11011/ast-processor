"""Multiple paragraphs integration tests."""

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.cli.main import main
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import W_NS


def _paragraph_texts(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    texts: list[str] = []
    for p in root.findall(f".//{{{W_NS}}}p"):
        t = p.find(f".//{{{W_NS}}}t")
        if t is not None and t.text:
            texts.append(t.text)
    return texts


def test_pipeline_multiple_paragraphs(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "multiple-paragraphs.md"
    output_path = tmp_path / "multiple-paragraphs.docx"
    convert_markdown_to_docx(input_path, output_path)

    texts = _paragraph_texts(output_path)
    assert texts == ["First paragraph.", "Second paragraph.", "Third paragraph."]


def test_cli_multiple_paragraphs(tmp_path: Path, fixtures_dir: Path):
    input_path = fixtures_dir / "multiple-paragraphs.md"
    output_path = tmp_path / "out.docx"
    code = main([str(input_path), "-o", str(output_path)])
    assert code == 0
    assert _paragraph_texts(output_path) == [
        "First paragraph.",
        "Second paragraph.",
        "Third paragraph.",
    ]


def test_each_paragraph_is_separate_w_p(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "out.docx"
    convert_markdown_to_docx(fixtures_dir / "multiple-paragraphs.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    paragraphs = [c for c in body if c.tag == f"{{{W_NS}}}p"]
    assert len(paragraphs) == 3
    for p in paragraphs:
        r = p.find(f"{{{W_NS}}}r")
        assert r is not None
        t = r.find(f"{{{W_NS}}}t")
        assert t is not None
        assert t.text
