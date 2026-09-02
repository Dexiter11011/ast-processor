# Plugins

md2docx supports trusted Python plugins that extend the conversion pipeline through a public API.

## Quick start

```bash
md2docx README.md \
  --plugin examples/plugins/notes_plugin.py \
  -o README.docx
```

Multiple plugins load in CLI order:

```bash
md2docx README.md \
  --plugin plugin_a.py \
  --plugin plugin_b.py \
  -o README.docx
```

## Security

Loading a plugin executes Python code in the current process with the same OS and user permissions as `md2docx`. Plugins are **not** sandboxed.

- Plugins load only from explicit `--plugin PATH` arguments (or programmatic API).
- Markdown content cannot load plugins (`<!-- plugin: ... -->` has no effect).
- Do not load untrusted plugin files.

## Example plugin

See [`examples/plugins/notes_plugin.py`](../examples/plugins/notes_plugin.py).

Markdown:

```markdown
<!-- note: Important -->
```

DOCX output:

```text
Note: Important
```

The same plugin registers:

- a custom AST node and handler
- a semantic style (`example.notes.note` → `ExampleNote`)
- a template region (`{{example_note}}`)
- a semantic validator (non-empty note text)

## Documentation

- [`PLUGIN_API.md`](PLUGIN_API.md) — public extension API reference
- [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md) — template placeholders and regions

## Unsupported in v1

- Arbitrary raw OOXML generation through the plugin API
- ZIP / package map access
- Remote plugin download
- Plugin dependency resolution
- Template scripting or loops
- Markdown-triggered plugin loading
