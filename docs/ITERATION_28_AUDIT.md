# Iteration 28 — Phase 1 Audit

Read-only audit validated against the codebase post Iteration 27 (690 pytest, 70 architecture, 62 golden, validate-docx PASS).

## Existing semantic abstractions

| Layer | Module | Notes |
|-------|--------|-------|
| Markdown AST | `md2docx.ast.types` | Frozen dataclasses for blocks and inline nodes |
| Caption models | `md2docx.captions.model` | `Figure`, `TableWithCaption`, `CrossReferenceBlock` (uses internal AST) |
| Inline state | `md2docx.processor.inline_formatting` | `InlineFormatting`, `RenderContext` |
| Style roles | `md2docx.styles.semantic` | Semantic constants resolved via `StyleManager` |
| Metadata | `md2docx.metadata.resolved` | Frozen `ResolvedDocumentMetadata` |
| OOXML facade | `md2docx.ooxml.api` | ~40 functions returning `lxml` elements |
| Document accumulator | `md2docx.ooxml.document` | `OoxmlDocument.body_children` is the de facto content fragment |

## Existing fragment model

- No `DocumentFragment` or `RichDocumentFragment` class exists.
- “Fragment” internally means `list[lxml.etree._Element]`.
- Plugin template regions: `FragmentRenderer = Callable[[ProcessingContext], list[Element]]`.
- Built-in handlers return `None` and mutate `ProcessingContext`.

## Existing composition model

- Blocks append to `OoxmlDocument.body_children`.
- Inline content uses `run_collector` during handler recursion.
- Template pipeline splices fragments via `TemplateCompositionPlan` and remaps IDs in `TemplateMerger`.

## Safe public candidates

Styled paragraphs with rich inline, line breaks, validated hyperlinks, whitelisted fields, path/bytes images, lists (NumberingManager-owned numId), read-only metadata, fragment composition.

## Unsafe internals

`md2docx.ast.*`, `ProcessingContext`/`AstProcessor` imports, collectors, raw lxml, numId/rId assignment, arbitrary field instructions, direct package access.

## Gaps

Plugins must assemble OOXML via Tier B `ooxml.api`; no inline composition API; bookmarks/fields/media/lists/captions require undocumented managers.

## Recommended Rich Semantic API

New Tier B module `md2docx.semantic` with immutable semantic value types, `SemanticContext` facade, internal `SemanticRenderer` adapter. Handlers may return `RichDocumentFragment` (backward compatible with void/OOXML paths). Tables deferred in v1.
