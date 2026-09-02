# Rendering Context

Iteration 8 introduces an explicit rendering model for inline Markdown → OOXML conversion.

## Problem

Previously, `StrongHandler` and `EmphasisHandler` collected nested runs and applied `api.bold()` / `api.italic()` **after** run creation. Formatting lived implicitly in finished `w:rPr` elements rather than in typed context state.

## Model

Two immutable dataclasses in `processor/inline_formatting.py`:

- **`InlineFormatting`** — `{ bold, italic, code }` with `with_bold()`, `with_italic()`, `with_code()`
- **`RenderContext`** — wraps `InlineFormatting`; `derive()` creates child context without mutating parent

`ProcessingContext.render_context` holds the current state. Handlers use `push_render_context()` to scope formatting to AST subtrees.

## Handler rules

| Handler | Behavior |
|---------|----------|
| `TextHandler` | `api.run_from_formatting(text, context.render_context.formatting)` |
| `StrongHandler` | Derive `with_bold()`, process children |
| `EmphasisHandler` | Derive `with_italic()`, process children |
| `InlineCodeHandler` | Derive `with_code()`, resolve Code character style |
| `LinkHandler` | Same render context for children; one external rel via `RelationshipManager` |

Strong/Emphasis must **not** call `api.bold()` / `api.italic()` directly.

## OOXML layer

`ooxml/run_format.py`:

- `run_from_formatting(text, formatting, *, r_style="")` — build `w:r` at emission time
- `apply_inline_formatting(run, formatting, *, r_style="")` — apply state to existing run

`api.run_from_formatting` is the handler-facing entry point.

## Non-goals (this iteration)

- Run merging / coalescing adjacent runs with identical formatting
- New Markdown features
- Changes to `AstProcessor`, parser, or AST types

## Tests

- `tests/processor/test_render_context.py` — unit tests for derive/isolation
- `tests/elements/test_formatting_leakage.py` — bold/italic must not leak across siblings
- `tests/fixtures/inline-formatting-matrix.md` — exhaustive inline fixture
- `tests/architecture/test_layer_boundaries.py` — handlers must not call `api.bold`/`api.italic`

## Related

Document-level styles (Heading1, Quote, Normal) are handled by the **Style System** — see [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md). Render Context covers inline formatting only.
