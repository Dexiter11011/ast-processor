# Plugin API migration guide

This document describes how to build and maintain plugins against **Plugin API v1** (`PLUGIN_API_VERSION = "1"`).

## Supported imports

### Tier A — `md2docx.plugin_api`

Import only symbols exported in `md2docx.plugin_api.__all__`:

- `Plugin`, `PluginMetadata`, `PluginRegistry`, `PLUGIN_API_VERSION`
- `DirectiveDefinition`, `TemplateRegionDefinition`, `ValidatorDefinition`, `ValidationPhase`
- `PluginError`, `PluginLoadError`, `DuplicateRegistrationError`, `RegistryFrozenError`, `UnsupportedApiVersionError`, `InvalidPluginNameError`, `ReservedNameError`

See [`API.md`](API.md) for the full manifest.

### Tier B — plugin adjuncts

These modules are stable for plugins but are not re-exported from `plugin_api`:

- `md2docx.styles.definition` — `StyleDefinition`, `ParagraphStyle`, `RunStyle`
- `md2docx.semantic` — Rich Semantic API (preferred for rendering)
- `md2docx.ooxml.api` — legacy OOXML builders (still supported)

### Do not import

The following are **internal** and may change without notice:

- `md2docx.processor.*` (including `ProcessingContext`, `AstProcessor`)
- `md2docx.parser.*`
- `md2docx.templates.merger`, `md2docx.templates.composer`
- `md2docx.ooxml.paragraph`, `md2docx.ooxml.run`, `lxml`

Handler methods receive `context` and `processor` at runtime. Type them as `Any`. Prefer returning `RichDocumentFragment` from handlers instead of building OOXML manually.

## Rich Semantic API migration

**Before (legacy OOXML path):**

```python
from md2docx.ooxml import api

style_id = context.styles.to_ooxml(STYLE_ID)
paragraph = api.paragraph([api.run(f"Note: {node.text}")], style_id=style_id)
context.document.add_body_element(paragraph)
```

**After (Rich Semantic API):**

```python
from md2docx.semantic import bold, fragment, paragraph, text

return fragment(
    paragraph(STYLE_ID, bold(text("Note: ")), text(node.text))
)
```

Template regions may return `RichDocumentFragment` instead of `list[Element]`.

## Entry point

Expose a module-level `plugin` object or a `get_plugin()` function that returns an object implementing:

```python
class Plugin(Protocol):
    @property
    def metadata(self) -> PluginMetadata: ...
    def register(self, registry: PluginRegistry) -> None: ...
```

Load with:

```bash
md2docx input.md --plugin path/to/plugin.py -o output.docx
```

## Naming rules

- Plugin name: dotted identifier, e.g. `example.notes`
- Handler AST types, styles, directives, validators, and template regions must be namespaced under the plugin name
- Core reserved names (e.g. `paragraph`, `heading`) cannot be registered

## Registry lifecycle

1. `PluginRegistry.empty()`
2. Load plugins in CLI order; each calls `register()`
3. Registry freezes before parsing
4. Duplicate registrations raise `DuplicateRegistrationError`
5. Registration after freeze raises `RegistryFrozenError`

## Error handling

Public plugin errors expose a stable `code` attribute. Contract tests assert **type** and **code**, not full message strings.

| Exception | `code` |
|-----------|--------|
| `PluginLoadError` | `plugin_load_error` |
| `DuplicateRegistrationError` | `duplicate_registration` |
| `RegistryFrozenError` | `registry_frozen` |
| `UnsupportedApiVersionError` | `unsupported_api_version` |
| `InvalidPluginNameError` | `invalid_plugin_name` |
| `ReservedNameError` | `reserved_name` |

## Validation phases

| Phase | When it runs |
|-------|----------------|
| `PARSE` | After Markdown → AST |
| `SEMANTIC` | During AST processing |
| `RENDER` | After OOXML body is built |
| `PACKAGE` | Reserved; not wired in v1 pipeline |

## Canonical examples

- Full example: [`examples/plugins/notes_plugin.py`](../examples/plugins/notes_plugin.py)
- Rich composition: [`examples/plugins/rich_content_plugin.py`](../examples/plugins/rich_content_plugin.py)
- Contract fixture (legacy OOXML): [`tests/contracts/plugins/basic_plugin.py`](../tests/contracts/plugins/basic_plugin.py)

## Upgrading to API v2

When `PLUGIN_API_VERSION` increments:

1. Set `api_version` in your `PluginMetadata` to match
2. Read the release notes for renamed or removed registration methods
3. Run contract tests: `pytest tests/contracts/`

Breaking changes to Tier A or Tier B symbols require a new API version. Additive changes (new optional registration hooks) may remain within v1.

## Security

Plugins are loaded only via `--plugin`. Markdown comments such as `<!-- plugin: ... -->` **do not** load code. Treat `--plugin` paths as trusted, same as running arbitrary Python.
