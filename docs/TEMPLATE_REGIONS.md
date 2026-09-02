# Template Navigation Regions

Iteration 25 adds typed template regions for navigation blocks alongside the existing `{{content}}` insertion point.

## Region placeholders

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

Navigation regions render Word field paragraphs using the same stack as Markdown directives (`TocManager`, existing handlers). No second rendering engine is introduced.

## Rules

| Region | Uniqueness | Behavior |
|--------|------------|----------|
| `{{content}}` | Exactly one (required) | Full Markdown body fragment |
| `{{toc}}` | Duplicates allowed | TOC field (levels 1–3) |
| `{{list_of_figures}}` | Duplicates allowed | LOF field |
| `{{list_of_tables}}` | Duplicates allowed | LOT field |
| Scalars | Duplicates allowed | In-place text replacement |

Additional constraints:

- Placeholder must be the only text in its paragraph (split runs are OK)
- Inline placeholders (`Project: {{title}}`) → error
- Unknown placeholders → error
- Header/footer regions are **not supported** in v1 (only direct `w:body` paragraphs are scanned)
- No expressions, filters, or scripting

## Template ordering

Regions are composed in **template document order**. A template may place navigation before or after content:

```text
Title:
{{title}}

{{content}}

Appendix navigation
{{toc}}
{{list_of_figures}}
```

Word resolves TOC/LOF/LOT fields at open/update time against the full merged document, so navigation regions may appear before generated content in the template.

## Dedup policy: template wins

When a template contains a navigation region, matching Markdown directives are stripped from the AST **before** content rendering:

| Template region | Stripped Markdown directive |
|-----------------|----------------------------|
| `{{toc}}` | `<!-- toc -->` / `TableOfContents` |
| `{{list_of_figures}}` | `<!-- lof -->` / `ListOfFigures` |
| `{{list_of_tables}}` | `<!-- lot -->` / `ListOfTables` |

This prevents duplicate navigation blocks when both template and Markdown specify the same region.

## Architecture

```text
Template DOCX
    ↓ scan regions
Markdown AST
    ↓ strip navigation nodes for template regions
AstProcessor → content fragment (body_children)
    +
TocManager → navigation fragments (on demand)
    ↓
TemplateMerger (single remapping pass on content fragment)
    ↓
TemplateComposer (multi-region compose, back-to-front insertion)
    ↓
Final DOCX
```

Key components:

| Module | Role |
|--------|------|
| `templates/regions.py` | `TemplateRegionKind` enum |
| `templates/placeholders.py` | `PlaceholderKind.NAVIGATION` registry |
| `templates/composition_plan.py` | `TemplateCompositionPlan` |
| `templates/composition.py` | Navigation fragment rendering |
| `templates/composer.py` | Multi-region compose |
| `parser/navigation_transform.py` | AST deduplication |

## Backward compatibility

Existing templates with only `{{content}}` and scalar placeholders behave exactly as in Iteration 17/18. The `{{ content }}` form (with internal whitespace) is now accepted consistently by scan and insertion.

## Building region fixtures

```bash
PYTHONPATH=src python scripts/build-template-fixtures.py
```

Creates:

- `tests/fixtures/templates/regions-basic.docx` — `{{toc}}` + `{{content}}`
- `tests/fixtures/templates/regions-navigation.docx` — TOC + LOF + LOT + `{{content}}`
- `tests/fixtures/templates/regions-complex.docx` — scalars, content before navigation

See also [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md) and [`NAVIGATION.md`](NAVIGATION.md).
