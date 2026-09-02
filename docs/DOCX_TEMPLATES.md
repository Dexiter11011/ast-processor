# DOCX Templates

Iteration 17 adds external DOCX templates and the `--template` CLI flag.

Iteration 18 adds scalar template placeholders and document context metadata.

Iteration 25 adds navigation template regions (`{{toc}}`, `{{list_of_figures}}`, `{{list_of_tables}}`). See [`TEMPLATE_REGIONS.md`](TEMPLATE_REGIONS.md).

## Template vs Theme vs Document Context

| Concept | Role |
|---------|------|
| **Template** | Base DOCX package (structure, Word styles, headers/footers, sections, media) |
| **Theme** | Visual token configuration (YAML) that affects `styles.xml` |
| **DocumentContext** | User/document data for placeholders and core properties |

They are separate:

```text
Template          = physical DOCX structure
Theme             = visual configuration
DocumentContext   = title, author, date, subject, keywords
```

## Architecture

```text
Template DOCX
    ↓
DocxPackageReader
    ↓
TemplatePackage
    +
Markdown → AST → DocumentFragment (OoxmlDocument.body_children)
    +
DocumentContext
    ↓
TemplateComposer (placeholder scan/validate/replace + insertion + remapping)
    ↓
Final DOCX package
```

Optional theme layer:

```text
Template styles.xml
    +
Theme styles (merge/override)
    ↓
Merged styles.xml
```

## Usage

```bash
md2docx README.md --template examples/templates/corporate.docx -o README.docx
```

With theme:

```bash
md2docx README.md \
  --template examples/templates/corporate.docx \
  --theme examples/themes/corporate.yaml \
  -o README.docx
```

With placeholders:

```bash
md2docx README.md \
  --template examples/templates/placeholders.docx \
  --title "Project Documentation" \
  --author "John Doe" \
  --date "2026-08-31" \
  -o README.docx
```

## Placeholders

Supported standalone paragraph placeholders:

```text
{{content}}
{{toc}}
{{list_of_figures}}
{{list_of_tables}}
{{title}}
{{author}}
{{date}}
{{subject}}
{{keywords}}
```

Example template body:

```text
Title:
{{title}}

Author:
{{author}}

Date:
{{date}}

{{content}}
```

Rules:

- Placeholder must be the only text in its paragraph (split runs are OK)
- `{{content}}` must appear exactly once
- Navigation regions (`{{toc}}`, `{{list_of_figures}}`, `{{list_of_tables}}`) may appear zero or more times
- Scalar placeholders may appear multiple times (same value)
- Unknown placeholders → error
- Missing required values → error
- Inline placeholders (`Project: {{title}}`) → error
- No expressions, filters, or scripting

## Document Context

Values are populated from:

1. CLI flags (`--title`, `--author`, `--date`) — highest precedence
2. Markdown YAML front matter — fallback for title/author/subject/keywords

`{{date}}` requires an explicit `--date` value. The engine does not use the system clock for placeholder dates.

Core properties (`docProps/core.xml`) are synchronized from the same document context for title, author, subject, and keywords.

## Content insertion point

Templates must contain exactly **one standalone paragraph**:

```text
{{content}}
```

Example:

```text
Introduction

{{content}}

Signature
```

Rules:

- Placeholder must be the only text in its paragraph (split runs are OK)
- Missing placeholder → error
- Multiple `{{content}}` placeholders → error
- Inline placeholder (`Hello {{content}}`) → error

## Precedence

| Combination | Result |
|-------------|--------|
| no template, no theme | Default greenfield DOCX (Iter 15 default) |
| template only | Template package + inserted content; template `styles.xml` |
| theme only | Theme-driven `styles.xml` (Iter 16) |
| template + theme | Template shell preserved; theme merges into template styles |
| template + metadata flags | Placeholders replaced; core props updated when title/author/subject/keywords present |

Section/header/footer directives in Markdown are **not supported** with `--template` (template headers/footers are preserved).

## Package preservation

The merger preserves template parts including:

- `word/settings.xml`, `word/fontTable.xml`, `word/theme/*` (if present)
- Template headers and footers
- Template media
- Unknown extra parts

Generated content adds:

- Inserted body blocks at `{{content}}`
- Scalar placeholder text replacement in template body
- New relationships (remapped rIds)
- New media (with collision-safe filenames)
- Merged numbering definitions (remapped numIds)
- Generated bookmark IDs remapped above template max ID
- Generated bookmark **names** remapped on collision (`architecture` → `architecture-1`); template bookmarks preserved

### Bookmark name collision policy

When generated content contains a bookmark with the same name as a template bookmark:

1. Template bookmark keeps its original name
2. Generated bookmark receives a deterministic suffix (`-1`, `-2`, …)
3. Generated REF fields and internal hyperlinks in the fragment are rewritten to the new name
4. Template REF fields are not modified

See [`NAVIGATION.md`](NAVIGATION.md) for full navigation architecture.

## Building template fixtures

```bash
PYTHONPATH=src python scripts/build-template-fixtures.py
```

Creates:

- `tests/fixtures/templates/minimal.docx`
- `tests/fixtures/templates/corporate.docx`
- `tests/fixtures/templates/corporate-navigation.docx` (TOC + LOF + LOT + `{{content}}`)
- `tests/fixtures/templates/navigation-collision.docx` (bookmark collision test fixture)
- `tests/fixtures/templates/placeholders-basic.docx`
- `tests/fixtures/templates/placeholders-formatting.docx`
- `tests/fixtures/templates/regions-basic.docx`
- `tests/fixtures/templates/regions-navigation.docx`
- `tests/fixtures/templates/regions-complex.docx`
- `examples/templates/corporate.docx`
- `examples/templates/placeholders.docx`

See also [`THEMES.md`](THEMES.md), [`EXTERNAL_THEMES.md`](EXTERNAL_THEMES.md), [`TEMPLATE_REGIONS.md`](TEMPLATE_REGIONS.md), and [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) for the distinction between static placeholders and dynamic Word fields.
