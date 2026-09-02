# Figures, Captions, Sequences & Cross-References

Iteration 20 adds semantic figure/table captions with Word field-based numbering and cross-references.

## Architecture

```text
Image
  ↓
Figure (semantic)
  ↓
Caption paragraph
  ↓
SEQ Figure field
  ↓
Bookmark (figure-{slug})
  ↓
REF field (with \r \h switches)
```

```text
Table
  ↓
TableWithCaption (semantic)
  ↓
Caption paragraph (above table)
  ↓
SEQ Table field
  ↓
Bookmark (table-{slug})
  ↓
REF field
```

## Separation of concerns

| Mechanism | Role |
|-----------|------|
| Caption text | Human-readable description after the sequence number |
| SEQ field | Word computes 1, 2, 3… per sequence name |
| Bookmark | Stable anchor for REF (`figure-architecture`, not `figure-1`) |
| REF field | Inserts sequence number from bookmark at reference site |
| Caption style | Theme-driven presentation (italic, smaller) |

**Caption text ≠ SEQ number ≠ Bookmark ≠ REF ≠ static number**

The application never increments `figure_number` counters. Word evaluates `SEQ Figure` / `SEQ Table` on open.

## Semantic model

Package: `md2docx.captions`

| Type | Purpose |
|------|---------|
| `CaptionKind` | `FIGURE`, `TABLE` |
| `SequenceKind` | Maps to Word SEQ names `"Figure"`, `"Table"` |
| `Caption` | `kind` + `text` (no `number` field) |
| `Figure` | `image` + optional `caption` |
| `TableWithCaption` | `table` + optional `caption` |
| `CrossReference` | `target`, `kind`, `prefix` |
| `SequenceManager` | Identity/labels only — **not** a counter |
| `CaptionService` | Renders figures, tables, cross-references |

## OOXML caption structure

```text
w:p [Caption style]
├── w:bookmarkStart
├── "Figure "
├── SEQ Figure (complex field)
├── ". "
├── caption text runs
└── w:bookmarkEnd
```

Cross-reference paragraph:

```text
w:p [Normal]
├── "See "
├── "Figure "
└── REF figure-bookmark \r \h
```

- `\r` — insert relative sequence number from bookmark
- `\h` — hyperlink to bookmark

Heading REF fields (Iteration 19) keep `\h` only.

## Placement defaults

| Object | Order |
|--------|-------|
| Figure | Image → Caption (below) |
| Table | Caption → Table (above) |

## Bookmark naming

Derived from caption text via `slugify()`:

| Caption text | Bookmark |
|--------------|----------|
| Architecture overview | `figure-architecture-overview` |
| Configuration values | `table-configuration-values` |

Duplicates get numeric suffix: `figure-architecture-1`.

## Internal API (Markdown syntax deferred)

Build AST programmatically and convert:

```python
from pathlib import Path
from md2docx.pipeline import convert_ast_to_docx
from tests.figures_fixtures import build_interleaved_figures_tables_document

doc = build_interleaved_figures_tables_document()
convert_ast_to_docx(doc, Path("out.docx"), source_dir=Path("tests/fixtures"))
```

Registered handlers:

| AST type | Handler |
|----------|---------|
| `figure` | `FigureHandler` |
| `table_with_caption` | `TableWithCaptionHandler` |
| `cross_reference` | `CrossReferenceHandler` |

## Styles

Semantic style `caption` → OOXML `Caption` (italic, 9pt, spacing after 120 twips).

Both figure and table captions share one Caption style; kind is semantic, not a separate style.

## Validation

- REF targets must exist in `BookmarkManager` at conversion time
- `ReferenceManager` validates typed cross-references (figure REF must target a figure bookmark)
- `NavigationRegistry` tracks semantic targets in document order
- Package validator cross-checks REF instructions against `w:bookmarkStart` names
- Invalid bookmark/sequence names rejected by field parser whitelist

## Related docs

- [`NAVIGATION.md`](NAVIGATION.md) — NavigationRegistry, LOF/LOT, template remapping
- [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) — SEQ, REF field details
- [`REFERENCES_AND_TOC.md`](REFERENCES_AND_TOC.md) — heading bookmarks and hyperlinks
- [`THEMES.md`](THEMES.md) — Caption style in theme system

## Remaining (post-Iteration 21)

- Markdown caption DSL (block directive or emphasis paragraph)
- Image `title` attribute as caption source
- Full Figure/Table label localization
