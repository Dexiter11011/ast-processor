# Error Handling

Production error UX for the md2docx CLI and library.

## Exit codes

| Code | Meaning | Examples |
|------|---------|----------|
| 0 | Success | Conversion completed |
| 1 | Usage / input configuration | Missing input, input is a directory, output is a directory, same input/output path |
| 2 | Processing / output failure | Invalid theme, bad plugin, parse error, missing image, validation failure, I/O error |

The CLI prints errors to **stderr** with the prefix `Error: `.

## Stable error codes

Plugin and semantic APIs expose machine-readable `code` attributes on their exception types. See [`API.md`](API.md) and [`PLUGIN_MIGRATION.md`](PLUGIN_MIGRATION.md).

## Atomic output guarantee

DOCX output is written through an atomic writer:

1. Bytes are written to a hidden temp file in the output directory (`.{name}.md2docx-{token}.tmp`).
2. When `--validate` is set, validation runs on temp bytes **before** replace.
3. On success, `os.replace` atomically updates the final path.
4. On failure, the temp file is removed and any existing output file is **preserved**.

This applies to both plain and template conversion paths.

## `--debug`

Use `--debug` to print a full Python traceback for **unexpected** internal errors (bugs). Known domain errors (parse, theme, plugin, etc.) never print tracebacks.

## Library vs CLI

- **CLI** — catches exceptions, maps them to diagnostics, returns exit codes. Never raises to the shell except via `SystemExit`.
- **Library** (`convert_markdown_to_docx`, etc.) — raises domain exceptions directly. Embedders should handle errors explicitly; no `sys.exit()` in the pipeline.

## Pre-flight I/O checks

Before conversion, the CLI validates:

- Input exists and is a regular file (not a directory)
- Output path is not an existing directory
- Resolved input and output paths differ

Parent directories for the output path are still created automatically on write (unchanged).
