# Production Readiness Audit

Audit of the md2docx Markdown → DOCX pipeline. **No new Markdown elements** were added.

## Before

| Metric | Value |
|--------|-------|
| Tests | 200 passed |
| Handlers | 16 registered |
| Markdown fixtures | 24 |
| DOCX validator | present (10 categories) |
| CLI `--validate` | not present |
| Missing image | silent skip |
| Path security | `../` allowed |
| AST JSON fixtures | none |
| Performance baseline | none |

## Changes

1. **`md2docx --validate`** — convert then run `validate_docx()`; exit 2 on failure
2. **Image errors** — `ImageNotFoundError` / `ImagePathError`; fail fast; path sandbox under `source_dir`
3. **AST JSON fixtures** — `tests/fixtures/ast/*.md` + `*.ast.json` + parser snapshot tests
4. **Handler tests** — `list_item`, `table_row`, `table_cell` dedicated unit tests
5. **Audit integration tests** — nested formatting, lists, links, images (PNG/JPEG/dual), tables, malformed input, unicode
6. **LibreOffice gate** — optional headless DOCX→PDF test (skip if not installed)
7. **Architecture tests** — ooxml/validation layer import guards extended
8. **Performance baseline** — `scripts/benchmark.py` → `out/BENCHMARK.md`
9. **Documentation** — README (Testing, Supported Markdown, Known limitations, Word checklist), `docs/TEST_MATRIX.md`

## Tests

| | Before | After |
|---|--------|-------|
| Total | 200 | **238** |

## Validation

| Check | Status |
|-------|--------|
| ZIP | PASS (all fixtures + `--validate`) |
| XML | PASS |
| Relationships | PASS |
| Content Types | PASS |
| Unicode | PASS (`unicode.md` fixture) |
| Images | PASS (PNG, JPEG, dual; missing → error) |
| Lists | PASS (audit + ordered restart) |
| Tables | PASS |
| Nested formatting | PASS |

## LibreOffice

SKIPPED unless `libreoffice` / `soffice` is on PATH — see `tests/integration/test_libreoffice_compat.py`.

## Performance

| Size | parse | process | package | total | peak MB |
|------|-------|---------|---------|-------|---------|
| 10 KB | 0.009s | 0.001s | 0.002s | 0.012s | 0.4 |
| 100 KB | 0.078s | 0.005s | 0.002s | 0.084s | 0.6 |
| 1 MB | 0.584s | 0.030s | 0.008s | 0.623s | 6.8 |

Run: `python scripts/benchmark.py`

## Remaining Risks

1. Microsoft Word compatibility not automated — manual checklist required
2. Malformed markdown (unclosed emphasis) accepts parser output without strict spec compliance
3. No lint/typecheck in CI (ruff/mypy not configured)
4. Golden snapshots omit `integration-article` / `all-iterations` (large files; validated structurally instead)

## Known Limitations

See README § Known limitations. Footnotes, HTML, task lists, etc. remain out of scope.

## Quality gate

```bash
pytest -q                         # 238 passed
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py
```

Lint/typecheck: not configured (documented gap).
