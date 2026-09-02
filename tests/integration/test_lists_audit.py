"""Lists audit — numbering, nesting, inline formatting."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx
from tests.helpers import W_NS


def _list_paragraphs(root: etree._Element) -> list[etree._Element]:
    result = []
    for p in root.findall(f".//{{{W_NS}}}p"):
        p_pr = p.find(f"{{{W_NS}}}pPr")
        if p_pr is None:
            continue
        style = p_pr.find(f"{{{W_NS}}}pStyle")
        if style is not None and style.get(f"{{{W_NS}}}val") == "ListParagraph":
            result.append(p)
    return result


def test_lists_audit(tmp_path: Path):
    source = tmp_path / "lists.md"
    source.write_text(
        "\n".join(
            [
                "- One",
                "- Two",
                "- Three",
                "",
                "1. First",
                "2. Second",
                "",
                "- Outer",
                "  - Nested one",
                "  - Nested two",
                "",
                "- **Bold**",
                "- *Italic*",
                "- `code`",
                "- [Link](https://example.com)",
                "",
                "1. First",
                "   - nested",
                "   - nested",
                "2. Second",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "lists.docx"
    convert_markdown_to_docx(source, output)
    report = validate_docx(output)
    assert report.ok, report.format_messages()

    with zipfile.ZipFile(output, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        assert "word/numbering.xml" in zf.namelist()

    list_ps = _list_paragraphs(root)
    assert len(list_ps) >= 10
    num_ids = {
        p.find(f".//{{{W_NS}}}numId").get(f"{{{W_NS}}}val")
        for p in list_ps
        if p.find(f".//{{{W_NS}}}numId") is not None
    }
    assert len(num_ids) >= 2
