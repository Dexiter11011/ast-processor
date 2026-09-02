# Test Matrix

Coverage by layer for supported Markdown features. Updated during Production Readiness Audit.

| Feature | Parser | AST fixture | Handler | OOXML | Package validate | Integration |
|---------|--------|-------------|---------|-------|------------------|-------------|
| paragraph | yes | yes | yes | yes | yes | yes |
| heading | yes | yes | yes | yes | yes | yes |
| bold (strong) | yes | yes | yes | yes | yes | yes |
| italic (emphasis) | yes | yes | yes | yes | yes | yes |
| nested inline | yes | partial | yes | yes | yes | yes |
| inline code | yes | yes | yes | yes | yes | yes |
| link | yes | yes | yes | yes | yes | yes |
| autolink | yes | yes | yes | yes | yes | yes |
| reference link | yes | yes | yes | yes | yes | yes |
| strikethrough | yes | yes | yes | yes | yes | yes |
| task list | yes | yes | yes | yes | yes | yes |
| hard break | yes | yes | yes | yes | yes | yes |
| internal link | yes | no | yes | yes | yes | yes |
| heading bookmark | n/a | no | yes | yes | yes | yes |
| external link rels | n/a | no | yes | yes | yes | yes |
| TOC field | yes | no | yes | yes | yes | yes |
| multi-link | partial | no | yes | yes | yes | yes |
| unordered list | yes | yes | yes | yes | yes | yes |
| ordered list | yes | yes | yes | yes | yes | yes |
| nested list | yes | partial | yes | yes | yes | yes |
| mixed nested list | no | no | yes | yes | yes | yes |
| list restart | no | no | yes | yes | yes | yes |
| blockquote | yes | yes | yes | yes | yes | yes |
| horizontal rule | yes | no | yes | yes | yes | yes |
| code block | yes | yes | yes | yes | yes | yes |
| image PNG | yes | yes | yes | yes | yes | yes |
| image JPEG | no | no | yes | yes | yes | yes |
| dual images | no | no | yes | yes | yes | yes |
| table | yes | yes | yes | yes | yes | yes |
| table style (tblStyle) | n/a | n/a | yes | yes | yes | yes |
| table header (tblHeader) | yes | no | yes | yes | yes | yes |
| table formatting | yes | no | yes | yes | yes | yes |
| table merge | yes | no | yes | yes | yes | yes |
| metadata | yes | no | n/a | yes | yes | yes |
| XML escaping | partial | no | yes | yes | yes | yes |
| Unicode | partial | no | yes | yes | yes | yes |
| golden document.xml | n/a | n/a | n/a | yes | n/a | 39 cases |
| golden numbering.xml | n/a | n/a | n/a | yes | n/a | 3 list cases |
| lists + tables integration | n/a | yes | yes | yes | yes | yes |
| page break | yes | yes | yes | yes | yes | yes |
| section break | yes | yes | yes | yes | yes | yes |
| header / footer | yes | yes | yes | yes | yes | yes |
| A4 / Letter / landscape | n/a | yes | yes | yes | yes | yes |
| sections integration | n/a | yes | yes | yes | yes | yes |
| references integration | n/a | yes | yes | yes | yes | yes |
| gfm integration | n/a | yes | yes | yes | yes | yes |
| style system | n/a | n/a | yes | yes | yes | yes |
| document theme | n/a | n/a | n/a | yes | yes | yes |
| theme switching | n/a | n/a | yes | yes | yes | yes |
| golden theme styles.xml | n/a | n/a | n/a | yes | n/a | 2 themes |

## Not supported (by design)

footnotes, definition lists, raw HTML, bare URL linkify.

See [`docs/MARKDOWN_COMPATIBILITY.md`](docs/MARKDOWN_COMPATIBILITY.md) for the full matrix.

## Test commands

```bash
pytest -q
pytest tests/parser/test_ast_fixtures.py -q
pytest tests/validation/ -q
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py
```
