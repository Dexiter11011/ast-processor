# Style System

Iteration 9 introduces a data-driven Style System that separates Markdown semantics from visual presentation.

## Problem

Previously, `word/styles.xml` was built by hardcoded functions in `ooxml/styles.py`, while handlers used a thin `StyleManager` resolver. The two were not unified, and semantic roles were often identical to OOXML styleIds (`Heading1`, `Quote`, …).

## Architecture

```text
Markdown AST
     ↓
Element Handler (semantic role)
     ↓
StyleManager.resolve_semantic("heading", level=1)  →  "heading1"
StyleManager.to_ooxml("heading1")                  →  "Heading1"
     ↓
document.xml: <w:pStyle w:val="Heading1"/>
     ↓
StyleRegistry + DefaultTheme
     ↓
StylesXmlWriter → word/styles.xml
```

## Components

| Component | Location | Role |
|-----------|----------|------|
| `StyleDefinition` | `styles/definition.py` | Immutable paragraph/run properties |
| `StyleRegistry` | `styles/registry.py` | One semantic id → one definition |
| `DefaultTheme` | `styles/theme.py` | Built-in style set |
| `StyleManager` | `processor/style_manager.py` | Handler facade over registry |
| `StylesXmlWriter` | `ooxml/styles_xml_writer.py` | Serializes registry to XML |

## Semantic styles

| Semantic id | OOXML styleId | Used by |
|-------------|---------------|---------|
| `normal` | Normal | Paragraph |
| `heading1`–`heading3` | Heading1–Heading3 | Heading |
| `quote` | Quote | Blockquote |
| `code_block` | NoSpacing | Fenced code block |
| `inline_code` | Code | Inline code (character style) |
| `list_bullet` / `list_number` | ListBullet / ListNumber | Legacy styles in registry (not emitted by handlers) |
| `list_paragraph` | ListParagraph | All list item paragraphs |
| `table` | TableGrid | Tables via `w:tblStyle` |

## Style System ≠ Render Context

These are separate concepts:

**Style System** — what kind of document element is this?

```text
Heading1, Quote, Normal, NoSpacing
```

**Render Context** — what inline formatting is active?

```text
bold, italic, code
```

Example — `# **Hello**`:

```text
Paragraph style: Heading1   (Style System)
Run formatting:  bold=true  (RenderContext)
```

See also [`RENDERING_CONTEXT.md`](RENDERING_CONTEXT.md).

## Non-goals (this iteration)

- YAML/JSON themes, CLI `--theme`, DOCX templates
- New Markdown features

Document themes: see [`THEMES.md`](THEMES.md).

List numbering and table layout details: [`LISTS_AND_TABLES.md`](LISTS_AND_TABLES.md).

## Tests

- `tests/styles/` — registry, theme, inheritance
- `tests/elements/test_handler_semantic_styles.py` — handler role mapping
- `tests/integration/test_style_system_integration.py` — style + inline formatting
- `tests/golden/test_styles_xml.py` — default styles.xml snapshot
