# Iteration 21 — Document Navigation

Advanced document navigation layer: semantic targets, template bookmark remapping, TOC hardening, List of Figures / List of Tables, and typed cross-reference validation.

## Architecture

```text
                         Document Navigation
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
           Heading             Figure               Table
              │                   │                   │
           Anchor              Anchor              Anchor
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         NavigationRegistry
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
             TOC             List of Figures     List of Tables
```

## Separation of concerns

| Component | Responsibility | Must NOT know |
|-----------|---------------|---------------|
| `NavigationRegistry` | Semantic targets, document order, kinds | Raw XML, numId, rId |
| `BookmarkManager` | Create/own anchors (name + id) | TOC, LOF, LOT semantics |
| `ReferenceManager` | Resolve target → bookmark; validate kind | OOXML, Markdown |
| `FieldManager` | Render REF/TOC/SEQ/LOF/LOT fields | Markdown, navigation semantics |
| `TemplateMerger` | ID + name remapping infrastructure | Figure/Table semantics |
| `SequenceManager` | Sequence identity labels | NavigationRegistry internals |

## NavigationRegistry

Stores `NavigationTarget` entries in document order:

```python
NavigationTarget(
    kind=NavigationTargetKind.FIGURE,
    name="architecture",           # logical slug
    bookmark_name="figure-architecture",
    label="Figure",
    level=None,                    # headings only
)
```

Registration points:

- **Headings** — pre-scanned in `BookmarkManager.register_headings()` (also registers in `NavigationRegistry`)
- **Figures / Tables** — registered in `CaptionService._render_caption()` after bookmark creation

## Bookmark name policy

| Kind | Pattern | Example |
|------|---------|---------|
| Heading | `<slug>` | `architecture` |
| Figure | `figure-<slug>` | `figure-architecture` |
| Table | `table-<slug>` | `table-results` |

Sequence numbers are **not** included in bookmark names. Numbering is Word-side via `SEQ Figure` / `SEQ Table`.

## Template bookmark remapping

When merging generated content into a template:

1. Collect template bookmark names from `word/document.xml`
2. Remap generated bookmark IDs (offset above template max ID)
3. For generated names colliding with template names → rename with `-1` suffix (`architecture` → `architecture-1`)
4. Rewrite in generated fragment only: `w:name`, REF `instrText`, `w:anchor` on hyperlinks
5. Template bookmarks and template REF fields remain unchanged

Implemented in `templates/bookmark_remap.py` via `BookmarkRemapMap`.

## ReferenceManager

Typed cross-reference validation:

```python
# OK — figure bookmark, figure kind
CrossReference(target="figure-architecture", kind=CaptionKind.FIGURE)

# Error — table bookmark referenced as figure
CrossReference(target="table-results", kind=CaptionKind.FIGURE)
# → ReferenceKindMismatchError
```

Heading references use `kind=None` and `RefStyle.HEADING` (REF with `\h` only).

Figure/table references use `RefStyle.CAPTION` (REF with `\r \h`).

## TOC

Existing `TableOfContents` semantic object + Word field:

```text
TOC \o "{min}-{max}" \h \z \u
```

Programmatic API:

```python
from md2docx.ast.types import TableOfContents, Document

Document(children=[TableOfContents(min_level=1, max_level=3), ...])
```

## List of Figures / List of Tables

Semantic AST nodes:

```python
from md2docx.ast.types import ListOfFigures, ListOfTables

Document(children=[
    ListOfFigures(),   # → TOC \h \z \c "Figure"
    ListOfTables(),    # → TOC \h \z \c "Table"
    ...
])
```

Word resolves captions dynamically — no static list generation in Python.

## Programmatic fixtures

Use `convert_ast_to_docx()` with AST builders in `tests/navigation_fixtures.py` for tests without Markdown syntax.

## Validation

- `validate_navigation()` — every navigation target has a bookmark anchor
- `ReferenceManager.validate_pending_refs()` — typed REF validation at end of conversion
- Package validator — bookmark uniqueness, REF targets, TOC/LOF/LOT field whitelist

## Related docs

- [FIGURES_AND_REFERENCES.md](FIGURES_AND_REFERENCES.md) — captions, SEQ, REF
- [DYNAMIC_FIELDS.md](DYNAMIC_FIELDS.md) — field types and security
- [DOCX_TEMPLATES.md](DOCX_TEMPLATES.md) — template merge and bookmark remapping
