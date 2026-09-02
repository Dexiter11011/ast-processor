# Markdown Navigation DSL

Canonical HTML-comment directives for table of contents, lists of figures/tables, captions, and cross-references.

## Overview

Navigation features use **standalone HTML comments** on their own line (same pattern as `<!-- toc -->`, `<!-- pagebreak -->`, and field directives). The parser emits intermediate markers; `caption_transform` coalesces them into semantic AST nodes (`Figure`, `TableWithCaption`, `CrossReferenceBlock`, `ListOfFigures`, `ListOfTables`).

```text
Markdown → pre-scan directives → markdown-it → caption_transform → AstProcessor → DOCX
```

## Table of contents and lists

```markdown
<!-- toc -->
<!-- toc: 2-3 -->
<!-- lof -->
<!-- lot -->
```

| Directive | AST node | Word field |
|-----------|----------|------------|
| `<!-- toc -->` | `TableOfContents` (levels 1–3) | `TOC \o "1-3"` |
| `<!-- toc: 2-3 -->` | `TableOfContents` | `TOC \o "2-3"` |
| `<!-- lof -->` | `ListOfFigures` | `TOC \c "Figure"` |
| `<!-- lot -->` | `ListOfTables` | `TOC \c "Table"` |

Place directives after YAML front matter and before the main body. Update fields in Word with **Ctrl+A → F9**.

## Figure captions

The caption directive must immediately follow a standalone image line:

```markdown
![Architecture overview](architecture.png)

<!-- caption: figure Architecture overview -->
```

Produces a numbered figure caption and bookmark `figure-architecture-overview`.

## Table captions

The caption directive must immediately precede a GFM table:

```markdown
<!-- caption: table Configuration values -->

| Name | Value |
|------|-------|
| A    | 1     |
```

Produces bookmark `table-configuration-values`.

## Cross-references (block)

Reference a figure or table by logical slug:

```markdown
<!-- ref: figure architecture-overview -->
<!-- ref: figure architecture-overview prefix="See " -->
<!-- ref: table configuration-values prefix="See " -->
```

| Part | Meaning |
|------|---------|
| `figure` / `table` | Target kind |
| slug | Logical bookmark id (see below) |
| `prefix="..."` | Text before the reference number (default: `"See "`) |

### Slug normalization

Caption text is slugified for the bookmark name via `caption_bookmark_name()`:

| Caption text | Bookmark |
|--------------|----------|
| `Architecture overview` | `figure-architecture-overview` |
| `Configuration values` | `table-configuration-values` |

In `<!-- ref: ... -->`, you may use the logical slug (`architecture-overview`) or the full bookmark name (`figure-architecture-overview`).

Forward references are supported: a `<!-- ref: ... -->` may appear before the caption it targets.

## Heading references (existing syntax)

Heading links do **not** use the navigation DSL:

```markdown
[See Architecture](#architecture)

<!-- field: ref architecture -->
```

These resolve to heading bookmarks, not figure/table captions.

## Limitations (Iteration 22)

| Topic | Status |
|-------|--------|
| Caption text | Plain string inside the HTML comment only |
| Rich markdown in captions (`**bold**`) | Not supported |
| Image `title` attribute | Not treated as caption |
| Fenced `::: figure` blocks | Not supported |
| Inline `@figure[slug]` | Not supported |
| Inline images in paragraphs | Not promoted to `Figure` (standalone `![...](...)` lines only) |

## Errors

| Message | Cause |
|---------|-------|
| `figure caption directive must immediately follow an image` | Orphan or misplaced figure caption |
| `table caption directive must be immediately followed by a table` | Orphan or misplaced table caption |
| `Error at line N: ...` | CLI includes file path and line when available |

## Examples

- User guide (Russian): [`docs/user-docs/04-navigaciya-i-oglavlenie.md`](user-docs/04-navigaciya-i-oglavlenie.md)
- Runnable example: [`examples/markdown/navigation.md`](../examples/markdown/navigation.md)
- Test fixture: [`tests/fixtures/markdown/navigation/navigation-dsl.md`](../tests/fixtures/markdown/navigation/navigation-dsl.md)
