"""Code block parser tests."""

from md2docx.parser.markdown_parser import MarkdownParser


def test_code_block_parser():
    source = "```python\nprint(\"hello\")\n```"
    doc = MarkdownParser().parse(source)
    assert len(doc.children) == 1
    block = doc.children[0]
    assert block.type == "code_block"
    assert block.language == "python"
    assert block.value == 'print("hello")\n'
