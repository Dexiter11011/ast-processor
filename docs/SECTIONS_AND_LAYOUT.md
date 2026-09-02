# Sections, Page Layout, Headers & Footers

Iteration 11 adds document section structure separate from the Style System and NumberingManager.

## Four layers

```text
Style System     → paragraph/run/table appearance (Heading1, Normal, TableGrid)
NumberingManager → list numId/ilvl
SectionManager   → page layout, section breaks, headers/footers
Table OOXML      → grid, borders, cell layout
```

## Section model

```text
Section
├── PageLayout (PageSize, Orientation, optional PageMargins)
├── header_rel_id (optional)
└── footer_rel_id (optional)
```

Default document: **one A4 portrait section** with final `w:sectPr` on `w:body`.

Multi-section documents place inline `w:sectPr` on the **last paragraph** of each prior section; the final section uses body-level `w:sectPr`.

## Page break vs section break

| Feature | OOXML | Markdown directive |
|---------|-------|-------------------|
| Page break | `<w:br w:type="page"/>` | `<!-- pagebreak -->` |
| Section break | inline `w:sectPr` + new section | `<!-- section: landscape -->` |

Page break does **not** change section properties. Section break starts a new `Section` with its own layout and optional header/footer.

## Header / footer directives

```markdown
<!-- header: Document Title -->
<!-- footer: Page 1 -->
```

These set header/footer content for the **current section**. Header/footer parts reuse the same paragraph/run OOXML builders and `Normal` style — no separate HeaderParagraphStyle.

Package structure:

```text
word/document.xml
    ├── headerReference → word/header1.xml
    └── footerReference → word/footer1.xml
```

## Layout specs

Section directive examples:

| Directive | Result |
|-----------|--------|
| `<!-- section: a4 -->` | A4 portrait |
| `<!-- section: letter -->` | Letter portrait |
| `<!-- section: landscape -->` | A4 landscape |
| `<!-- section: a4 margins=720,720,720,720 -->` | A4 with custom margins (twips) |

Units: **twips** (1/1440 inch), consistent with OOXML `pgSz` / `pgMar`.

## Components

| Component | Location |
|-----------|----------|
| `PageLayout`, `Section` | `sections/definition.py` |
| `SectionManager` | `sections/manager.py` |
| `build_sect_pr()` | `ooxml/section.py` |
| Header/footer parts | `ooxml/header_footer.py` |
| Page break | `ooxml/page_break.py` |
| Block directives | `parser/block_directive.py` |

## Tests

- `tests/sections/` — layout model
- `tests/ooxml/test_section.py` — sectPr serialization
- `tests/integration/test_sections_layout.py` — page break, landscape, header/footer
- `tests/fixtures/sections-integration.md` — combined integration fixture

See also [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md), [`LISTS_AND_TABLES.md`](LISTS_AND_TABLES.md), [`RENDERING_CONTEXT.md`](RENDERING_CONTEXT.md).
