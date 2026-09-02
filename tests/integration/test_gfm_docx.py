"""GFM feature integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def _convert(fixture: Path, output: Path) -> etree._Element:
    convert_markdown_to_docx(fixture, output)
    with zipfile.ZipFile(output, "r") as zf:
        return etree.fromstring(zf.read("word/document.xml"))


def test_task_list_renders_checkbox_glyphs(tmp_path: Path):
    root = _convert(
        Path("tests/fixtures/markdown/gfm/task-list.md"),
        tmp_path / "task-list.docx",
    )
    texts = "".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "☐" in texts
    assert "☒" in texts
    assert "[ ]" not in texts
    assert "[x]" not in texts


def test_strikethrough_renders_w_strike(tmp_path: Path):
    root = _convert(
        Path("tests/fixtures/markdown/gfm/strikethrough.md"),
        tmp_path / "strikethrough.docx",
    )
    strikes = root.findall(f".//{{{W_NS}}}r/{{{W_NS}}}rPr/{{{W_NS}}}strike")
    assert len(strikes) >= 4
    texts = "".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "~~" not in texts


def test_hard_break_renders_w_br(tmp_path: Path):
    root = _convert(
        Path("tests/fixtures/markdown/gfm/hard-breaks.md"),
        tmp_path / "hard-breaks.docx",
    )
    assert len(root.findall(f".//{{{W_NS}}}br")) >= 2


def test_autolinks_use_hyperlink_pipeline(tmp_path: Path):
    output = tmp_path / "autolinks.docx"
    root = _convert(Path("tests/fixtures/markdown/gfm/autolinks.md"), output)
    hyperlinks = root.findall(f".//{{{W_NS}}}hyperlink")
    assert len(hyperlinks) >= 3
    for hyper in hyperlinks:
        assert hyper.get(f"{{{R_NS}}}id") is not None
    with zipfile.ZipFile(output, "r") as zf:
        rels = zf.read("word/_rels/document.xml.rels").decode()
    assert "https://example.com" in rels
    assert "mailto:user@example.com" in rels


def test_gfm_integration(tmp_path: Path, fixtures_dir: Path):
    output = tmp_path / "gfm-integration.docx"
    root = _convert(fixtures_dir / "gfm-integration.md", output)
    assert root.findall(f".//{{{W_NS}}}br")
    assert root.findall(f".//{{{W_NS}}}strike")
    assert root.findall(f".//{{{W_NS}}}hyperlink")
    texts = "".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "☒" in texts or "☐" in texts
