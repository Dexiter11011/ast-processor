# Iteration 30 — Phase 1 Audit

Read-only audit validated against the codebase post Iteration 28 (710 pytest, 75 architecture, 62 golden, validate-docx PASS).

## CLI entrypoint

- Module: `md2docx/cli/main.py`
- Exit owner: `main()` returns int; `sys.exit` only in `__main__`
- Error format: `Error: {message}` on stderr via `_error()`

## Exit codes (current)

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Missing input file |
| 2 | Theme/template/plugin preload failure, conversion error, validation failure, OSError |

## Exception handling

- 15+ typed `except` blocks in `main()` before Iteration 30
- No catch-all for unexpected errors (traceback in normal mode)
- Not handled: `NavigationError`, `SemanticError`, `FootnoteError` (runtime)

## Output writing

- `DocxPackageWriter._write_zip` writes directly to final path via `path.write_bytes()`
- No temporary file or atomic replace
- `--validate` runs after final write; corrupt output can remain on disk
- `output_path.parent.mkdir(parents=True, exist_ok=True)` auto-creates parent dirs

## Input/output validation gaps

- Input directory reported as "does not exist" (not "not a file")
- Output directory not rejected pre-flight
- Same input/output path not rejected
- Overwrite on success: allowed (preserved)

## Error hierarchies

| Domain | Base | Stable `code` |
|--------|------|---------------|
| Plugin | `PluginError` | Yes |
| Semantic | `SemanticError` | Yes |
| Theme | `ThemeError` | No |
| Template | `TemplateError` | No |
| Parser | `*ParseError` | No (line/path attrs) |
| Processor | various | No |

## Resource lifecycle

- Template reader: `with ZipFile` — OK
- Plugin loader: partial registry on mid-loop failure (not transactional)
- No logging module in md2docx core

## Iteration 30 targets

1. Unified CLI exception boundary with `--debug`
2. Atomic output writer (temp → validate → replace)
3. Pre-flight I/O validation
4. Transactional plugin loading
5. Contract tests for exit codes, atomicity, recovery
6. ERROR_HANDLING.md + RELEASE_READINESS.md
