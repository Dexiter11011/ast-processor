# Document Theme System

Iteration 15 introduces a pluggable **Document Theme** that controls visual presentation independently from Markdown parsing and element handlers.

## Architecture

```text
Markdown AST
     ↓
Semantic role (handlers)
     ↓
StyleManager
     ↑
DocumentTheme
     ↓
ThemeResolver → StyleRegistry
     ↓
StylesXmlWriter → word/styles.xml
```

Parallel inline path (unchanged):

```text
AST → RenderContext → InlineFormatting → run properties
```

## Ownership

| Component | Owns |
|-----------|------|
| `DocumentTheme` | visual tokens + semantic style configuration |
| `ThemeResolver` | Theme tokens → `StyleRegistry` |
| `StyleRegistry` | resolved semantic style definitions |
| `StyleManager` | style lookup for handlers |
| `StylesXmlWriter` | `StyleDefinition` → `styles.xml` |
| Handlers | semantic role selection only |
| `RenderContext` | local inline formatting (`bold`, `italic`, `strike`, `code`) |
| `NumberingManager` | `numId` / `ilvl` (not visual theme) |
| `SectionManager` | explicit section overrides over theme page defaults |

## Theme tokens

Themes configure presentation through immutable token groups in [`styles/tokens.py`](../src/md2docx/styles/tokens.py):

- `TypographyTokens` — body/heading/code fonts and sizes
- `ColorTokens` — text, heading, link, code, quote colors
- `SpacingTokens` — paragraph and heading spacing
- `HeadingScaleTokens` — heading level sizes
- `PageDefaultsTokens` — page size and optional margins
- `LinkPresentationTokens` — hyperlink underline style
- `TablePresentationTokens` — border and header emphasis defaults

## Built-in themes

| Theme | Location | Purpose |
|-------|----------|---------|
| `DefaultTheme` | `styles/theme.py` | Production default (Calibri, Word-like spacing) |
| `AlternativeTestTheme` | `tests/themes/alternative_test_theme.py` | Test-only theme switching verification |

## Theme ≠ RenderContext

**Theme** answers: what kind of document element is this (`Heading1`, `Quote`, `Normal`)?

**RenderContext** answers: what inline formatting is active (`bold`, `italic`)?

Example: `# **Hello**` → paragraph style `Heading1` (theme) + run `bold=true` (RenderContext).

## Theme ≠ Numbering

List bullet/ordered distinction uses `NumberingManager` and `w:numPr`. Theme may configure `ListParagraph` indent/spacing/font only.

## Theme ≠ Table Layout

Grid, colspan, rowspan, and cell widths remain in the table engine. Theme supplies border/header presentation tokens consumed by the OOXML table builder.

## Theme ≠ Section

Theme provides default page size (and optional margins via `PageDefaultsTokens.emit_margins`). Explicit section directives override via `SectionManager`.

## Precedence

```text
Built-in default
    ↓
Theme
    ↓
Explicit document configuration
    ↓
Explicit section configuration
    ↓
Local inline formatting (RenderContext)
```

## Theme switching

The same Markdown produces:

- **identical AST** (theme does not affect parsing)
- **identical semantic document structure** (same handlers, same `w:pStyle` roles)
- **different `styles.xml`** (fonts, sizes, colors from tokens)

```python
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.styles.theme import DefaultTheme
from tests.themes.alternative_test_theme import AlternativeTestTheme

convert_markdown_to_docx(source, out_a, theme=DefaultTheme.create())
convert_markdown_to_docx(source, out_b, theme=AlternativeTestTheme.create())
```

## External themes (YAML)

Iteration 16 adds external YAML themes via `ThemeLoader` and the CLI `--theme` flag.

```text
YAML
    ↓
ThemeLoader
    ↓
DocumentTheme
    ↓
ThemeResolver
    ↓
StyleRegistry
```

See [`EXTERNAL_THEMES.md`](EXTERNAL_THEMES.md) for the YAML schema, validation rules, and examples.

## DOCX templates

Iteration 17 adds DOCX templates via `DocxPackageReader` and the CLI `--template` flag.

```text
Template DOCX
    ↓
TemplatePackage
    +
Markdown content fragment
    ↓
TemplateMerger
    ↓
Final DOCX
```

See [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md). **Template ≠ Theme.**

## TODO

- **Caption** semantic style — implemented (Iteration 20; italic, 9pt; shared by figure and table captions)
- **`table_header` / `table_cell`** semantic styles — reserved, not in registry
- **Theme composition API** — basic `compose_tokens()` exists; full inheritance TBD
- **Per-heading colors** — all headings share `colors.heading` today

See also [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md).
