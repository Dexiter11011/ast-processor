# Document Metadata

Unified document metadata flow for md2docx.

## Overview

All document metadata resolves to a single canonical object:

```text
CLI + front matter + defaults
        ↓
MetadataResolver
        ↓
ResolvedDocumentMetadata
        ├── {{title}}, {{author}}, {{date}}, {{subject}}, {{keywords}}
        ├── docProps/core.xml (dc:title, dc:creator, dc:subject, cp:keywords)
        └── TITLE / AUTHOR field cached display (Word reads core props at open)
```

## Source precedence

Per field, highest priority wins:

```text
CLI  >  front matter  >  defaults
```

Template DOCX files do **not** provide metadata defaults. Pre-existing template `docProps` are preserved only when no resolved core-property values are supplied.

## Supported fields

| Field | Front matter | CLI | Placeholder | Core property |
|-------|--------------|-----|-------------|---------------|
| title | yes | `--title` | `{{title}}` | `dc:title` |
| author | yes | `--author` | `{{author}}` | `dc:creator` |
| date | yes | `--date` | `{{date}}` | no (see below) |
| subject | yes | `--subject` | `{{subject}}` | `dc:subject` |
| keywords | yes | `--keywords` | `{{keywords}}` | `cp:keywords` |

Keywords accept comma-separated values in front matter or CLI.

## Front matter

```markdown
---
title: Project Documentation
author: Ivan Petrov
date: 2026-08-31
subject: Example
keywords: markdown, docx
---
```

Supported keys: `title`, `author`, `date`, `subject`, `keywords`.

Configuration keys such as `theme:` and `template:` are ignored by the metadata parser.

Empty or whitespace-only values normalize to unset (`None`).

## CLI

```bash
md2docx README.md \
  --title "Final Documentation" \
  --author "John Doe" \
  --date 2026-08-31 \
  --subject "Technical spec" \
  --keywords "markdown, docx" \
  -o README.docx
```

CLI overrides front matter independently per field:

| Front matter | CLI | Result |
|--------------|-----|--------|
| title = A | `--title B` | title = B |
| author = Ivan | (none) | author = Ivan |

## Static date vs Word DATE field

| Mechanism | Behavior |
|-----------|----------|
| `date` metadata / `{{date}}` | Static value from CLI or front matter |
| Word `DATE` field | Dynamic; uses Word's date at field update |
| `dcterms:created` / `modified` | Package timestamps (explicit in tests; UTC now in production) |

Do not treat metadata `date` as the Word `DATE` field.

## Dynamic fields

| Field | Resolves from |
|-------|---------------|
| `TITLE` | `dc:title` in core properties |
| `AUTHOR` | `dc:creator` in core properties |
| `DATE` | Word system date (not metadata) |

Cached field display text uses resolved title/author when available.

## Architecture

| Component | Responsibility |
|-----------|----------------|
| `MetadataResolver` | Precedence, normalization (no OOXML) |
| `ResolvedDocumentMetadata` | Canonical resolved state |
| `DocumentContext` | Template placeholder view of resolved metadata |
| `build_core_props_xml` | Serialize resolved metadata to OOXML |
| `TemplateComposer` | Replace placeholders (no precedence logic) |
| `CLI` | Collect raw inputs only |

## Examples

- [`examples/markdown/metadata.md`](../examples/markdown/metadata.md)
- [`tests/fixtures/metadata-full.md`](../tests/fixtures/metadata-full.md)

See also [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) for field directives.
