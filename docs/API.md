# Public API Reference

md2docx separates **stable public contracts** from **internal implementation**. Only symbols listed in this document (or sub-documents linked below) are supported for external use.

## API tiers

### Tier A — Plugin API v1 (stable)

Namespace: `md2docx.plugin_api`

All Tier A symbols are listed in [`plugin_api/__init__.py`](../src/md2docx/plugin_api/__init__.py) `__all__` and mirrored in [`tests/contracts/api_manifest.json`](../tests/contracts/api_manifest.json).

Machine-readable manifest changes require an explicit update to the manifest and contract tests.

See [`PLUGIN_API.md`](PLUGIN_API.md) for usage details.

### Tier B — Plugin adjuncts (stable with plugin API v1)

These modules are stable for plugin authors but are not re-exported from `plugin_api`:

| Module | Symbols |
|--------|---------|
| `md2docx.styles.definition` | `StyleDefinition`, `ParagraphStyle`, `RunStyle` |
| `md2docx.ooxml.api` | Legacy OOXML builders (`paragraph`, `run`, `text`, …) |
| `md2docx.semantic` | Rich Semantic API (`RichDocumentFragment`, `paragraph`, `text`, `bold`, …) |

Handlers may return `RichDocumentFragment` from `process()` or template region renderers. Prefer `md2docx.semantic` for new plugins.

Handlers receive runtime objects from the engine (`context`, `processor`). Wrap with `SemanticContext.from_processing_context(context)` when calling `render()`. Do **not** import `md2docx.processor.*` in plugins.

## Rich Semantic API

Namespace: `md2docx.semantic` (Tier B)

Build document content as immutable semantic values, not raw OOXML:

```python
from md2docx.semantic import RichDocumentFragment, bold, fragment, paragraph, text

return fragment(
    paragraph("example.notes.note", bold(text("Note: ")), text("Important"))
)
```

Supported operations:

- Paragraphs with styled inline runs (`text`, `bold`, `italic`, `strike`, `inline_code`)
- `line_break()`, `hyperlink()`, `hyperlink_to()`
- Whitelisted fields (`page_field`, `title_field`, `ref_field`, …)
- `image()`, `figure()`, `cross_reference()`
- `bullet_list()`, `ordered_list()`
- `bookmark()` paragraphs
- Fragment composition via `+` and `fragment(...)`

Unsupported in v1: arbitrary OOXML, arbitrary field instructions, raw `numId`/`rId`, remote image URLs, semantic tables.

See [`ITERATION_28_AUDIT.md`](ITERATION_28_AUDIT.md) for design rationale.

### Tier C — CLI behavioral contract (stable)

| Aspect | Contract |
|--------|----------|
| Entry | `md2docx INPUT [-o OUTPUT]` |
| `--plugin PATH` | Repeatable; loads Python plugins in argument order |
| Exit codes | `0` success, `1` usage/input config, `2` conversion/validation errors |
| Errors | `Error: {message}` on stderr without traceback in normal mode |
| `--debug` | Full traceback for unexpected internal errors only |
| `--validate` | Validates temp output before atomic replace; preserves existing file on failure |
| I/O | Rejects input directories, output directories, and identical input/output paths |

See [`ERROR_HANDLING.md`](ERROR_HANDLING.md) and [`PLUGINS.md`](PLUGINS.md).

### Tier D — Programmatic integration (experimental)

These subpackages export symbols via `__all__` but are not yet versioned as strictly as Tier A:

- `md2docx.pipeline.convert_markdown_to_docx`
- `md2docx.metadata`
- `md2docx.themes`
- `md2docx.templates`
- `md2docx.validation`

Use for integration testing and tooling; expect slower stability guarantees than Tier A.

## Internal (unsupported)

Undocumented imports may break without notice:

```text
md2docx.parser.*
md2docx.processor.*
md2docx.elements.*
md2docx.templates.merger
md2docx.ooxml.* (except api facade)
md2docx.ast.*
md2docx.plugins.loader
```

## Compatibility policy

| Change type | Policy |
|-------------|--------|
| Additive Tier A symbol | Update manifest + docs + contract tests |
| Breaking Tier A change | Bump `PLUGIN_API_VERSION` |
| Internal refactor | Allowed if contract tests pass |
| OOXML/XML structure | May change if semantic behavior preserved |

## Error contract

Public plugin errors expose stable `code` attributes (see [`plugin_api/errors.py`](../src/md2docx/plugin_api/errors.py)). Contract tests assert exception **types** and **codes**, not full message strings.

| Exception | Code |
|-----------|------|
| `PluginLoadError` | `plugin_load_error` |
| `DuplicateRegistrationError` | `duplicate_registration` |
| `RegistryFrozenError` | `registry_frozen` |
| `UnsupportedApiVersionError` | `unsupported_api_version` |
| `InvalidPluginNameError` | `invalid_plugin_name` |
| `ReservedNameError` | `reserved_name` |

Naming validation failures (`InvalidPluginNameError`, `ReservedNameError`) collectively cover validation errors described as `PluginValidationError` in design docs.

## Contract tests

Run:

```bash
pytest tests/contracts/ -q
```

The manifest snapshot test fails if `plugin_api.__all__` changes without updating `api_manifest.json`.

## Related docs

- [`PLUGIN_API.md`](PLUGIN_API.md) — plugin extension reference
- [`PLUGIN_MIGRATION.md`](PLUGIN_MIGRATION.md) — API v1 migration notes
- [`ERROR_HANDLING.md`](ERROR_HANDLING.md) — exit codes, atomic output, `--debug`
- [`RELEASE_READINESS.md`](RELEASE_READINESS.md) — release checklist
