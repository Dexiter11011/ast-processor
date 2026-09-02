"""Hyperlink relationships audit."""

from __future__ import annotations

import zipfile
from pathlib import Path

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.validation import validate_docx


def test_multiple_links_have_unique_external_relationships(tmp_path: Path):
    source = tmp_path / "links.md"
    source.write_text(
        "\n".join(
            [
                "[A](https://a.example)",
                "[B](https://b.example?q=1&x=2)",
                "[C](https://c.example)",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "links.docx"
    convert_markdown_to_docx(source, output)
    assert validate_docx(output).ok

    with zipfile.ZipFile(output, "r") as zf:
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")

    assert rels.count('TargetMode="External"') == 3
    assert "https://b.example?q=1&amp;x=2" in rels
    ids = [line.split('Id="')[1].split('"')[0] for line in rels.splitlines() if 'Id="rId' in line]
    assert len(ids) == len(set(ids))
