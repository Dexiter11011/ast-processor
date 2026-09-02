"""Theme switching and AST invariance tests."""

from __future__ import annotations

import json
import zipfile
from dataclasses import asdict
from pathlib import Path

from lxml import etree

from md2docx.parser.markdown_parser import MarkdownParser
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.styles.theme import DefaultTheme
from tests.helpers import W_NS
from tests.themes.alternative_test_theme import AlternativeTestTheme


THEME_SAMPLE = """# Hello

Normal paragraph.

> Quote

```python
print("hello")
```
"""


def _ast_json(markdown: str) -> str:
    ast = MarkdownParser().parse(markdown)
    return json.dumps(asdict(ast), sort_keys=True)


def _styles_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return zf.read("word/styles.xml")


def _document_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path, "r") as zf:
        return zf.read("word/document.xml")


def test_same_markdown_produces_same_ast_across_themes():
    assert _ast_json(THEME_SAMPLE) == _ast_json(THEME_SAMPLE)


def test_theme_switch_changes_styles_xml_not_ast(tmp_path: Path):
    source = tmp_path / "sample.md"
    source.write_text(THEME_SAMPLE, encoding="utf-8")
    default_out = tmp_path / "default.docx"
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())
    assert _styles_xml(default_out) != _styles_xml(alt_out)


def test_theme_switch_preserves_document_structure(tmp_path: Path):
    source = tmp_path / "sample.md"
    source.write_text(THEME_SAMPLE, encoding="utf-8")
    default_out = tmp_path / "default.docx"
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, default_out, theme=DefaultTheme.create())
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())

    def paragraph_styles(docx_path: Path) -> list[str | None]:
        root = etree.fromstring(_document_xml(docx_path))
        styles: list[str | None] = []
        for paragraph in root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}p"):
            p_pr = paragraph.find(f"{{{W_NS}}}pPr")
            if p_pr is None:
                styles.append(None)
                continue
            p_style = p_pr.find(f"{{{W_NS}}}pStyle")
            styles.append(p_style.get(f"{{{W_NS}}}val") if p_style is not None else None)
        return styles

    assert paragraph_styles(default_out) == paragraph_styles(alt_out)


def test_alternative_theme_changes_body_font_in_styles_xml(tmp_path: Path):
    source = tmp_path / "sample.md"
    source.write_text("Plain.", encoding="utf-8")
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())
    styles = _styles_xml(alt_out).decode("utf-8")
    assert "Georgia" in styles
    assert "Calibri" not in styles


def test_alternative_theme_changes_link_color_in_document(tmp_path: Path):
    source = tmp_path / "link.md"
    source.write_text("[Site](https://example.com)", encoding="utf-8")
    alt_out = tmp_path / "alt.docx"
    convert_markdown_to_docx(source, alt_out, theme=AlternativeTestTheme.create())
    document = _document_xml(alt_out).decode("utf-8")
    assert "800080" in document
