# Plugin API Reference

Public namespace: `md2docx.plugin_api`

Internal modules (`md2docx.ooxml.*` builders, `md2docx.templates.merger`, full `ProcessingContext` mutation) are not part of the stable plugin contract.

## API version

```python
from md2docx.plugin_api import PLUGIN_API_VERSION  # "1"
```

Plugins declare `PluginMetadata.api_version = "1"`. Unsupported versions raise `UnsupportedApiVersionError`.

## Plugin interface

```python
from md2docx.plugin_api import PluginMetadata, PluginRegistry

class MyPlugin:
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="acme.demo", version="1.0.0")

    def register(self, registry: PluginRegistry) -> None:
        ...

plugin = MyPlugin()
```

Entry point for `--plugin PATH`: module-level `plugin` object (or `get_plugin()` callable).

## PluginRegistry

Facade over allowed extension types. Delegates to existing core registries where possible.

| Method | Purpose |
|--------|---------|
| `register_handler(type, handler)` | AST node type → `ElementHandler` |
| `register_style(StyleDefinition)` | Semantic style via `StyleRegistry` |
| `register_directive(DirectiveDefinition)` | HTML comment directive → AST |
| `register_template_region(TemplateRegionDefinition)` | Template placeholder → fragment |
| `register_validator(ValidatorDefinition)` | Phase-specific validation |
| `freeze()` | Lock registry before conversion |

After `freeze()`, all `register_*` calls raise `RegistryFrozenError`.

Duplicate registrations raise `DuplicateRegistrationError`.

## Namespace policy

| Resource | Example |
|----------|---------|
| Plugin name | `example.notes` |
| AST type | `example.notes.note` |
| Style semantic id | `example.notes.note` |
| Template region | `example_note` |
| Validator / directive name | `example.notes.validate_notes` |

Core names (`paragraph`, `content`, `toc`, …) are reserved.

## Handlers

Implement the existing handler protocol:

```python
def process(self, node, context, processor) -> None:
    ...
```

Use `md2docx.ooxml.api` builders and `context.document.add_body_element()`. Do not edit raw XML or ZIP parts.

## Directives

```python
DirectiveDefinition(
    name="example.notes.directive",
    pattern=re.compile(r'^\s*<!--\s*note:\s*(?P<text>.+?)\s*-->\s*$', re.I),
    to_ast=lambda match, line_no: CustomNote(text=match.group("text")),
)
```

Directives are matched on standalone lines after built-in directives.

## Template regions

```python
TemplateRegionDefinition(
    placeholder_name="example_note",
    render_fragment=lambda context: [...],
    strip_ast_types=frozenset({"example.notes.note"}),
)
```

Template wins over Markdown: when `{{example_note}}` is present, matching AST nodes are stripped from the content fragment before rendering.

## Validators

```python
from md2docx.plugin_api import ValidationPhase, ValidatorDefinition

ValidatorDefinition(
    name="example.notes.validate",
    phase=ValidationPhase.SEMANTIC,
    validate=lambda document: ...,
)
```

Phases:

| Phase | When |
|-------|------|
| `PARSE` | After Markdown → AST |
| `SEMANTIC` | After `process_document` walk, before navigation validation |
| `RENDER` | After rendering, before package write |
| `PACKAGE` | Reserved for future post-package hooks |

## CLI

```bash
md2docx input.md --plugin ./my_plugin.py -o output.docx
```

Load failures print `Error: ...` without a traceback in normal mode.

## Compatibility matrix

Supported:

- Custom AST nodes (namespaced dataclasses)
- Handlers
- Directives
- Semantic styles
- Template regions
- Validators (PARSE / SEMANTIC / RENDER)

Not supported:

- Arbitrary raw OOXML
- ZIP access
- Remote plugin loading
- Dependency resolver
- Navigation target registration (v1)
- Plugin sandboxing

## See also

- [`PLUGINS.md`](PLUGINS.md)
- [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md)
