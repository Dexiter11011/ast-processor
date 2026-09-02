"""Table parser tests."""

from pathlib import Path

from md2docx.parser.markdown_parser import MarkdownParser


def test_table_parser():
    source = "| Name | Age |\n|------|-----|\n| Bob | 20 |\n| Ann | 30 |"
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 1
    table = doc.children[0]
    assert table.type == "table"
    assert len(table.rows) == 3
    assert table.rows[0].header is True
    assert table.column_aligns == ["", ""]
    assert table.borders == "single"
    assert [cell.children[0].children[0].value for cell in table.rows[0].cells] == ["Name", "Age"]
    assert [cell.children[0].children[0].value for cell in table.rows[1].cells] == ["Bob", "20"]
    assert [cell.children[0].children[0].value for cell in table.rows[2].cells] == ["Ann", "30"]


def test_table_variants_skips_directive_paragraphs(fixtures_dir: Path):
    source = (fixtures_dir / "table-variants.md").read_text(encoding="utf-8")
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 4
    assert all(block.type == "table" for block in doc.children)
    assert [block.borders for block in doc.children] == ["single", "single", "none", "double"]
