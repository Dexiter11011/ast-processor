# Dynamic DOCX Fields

Iteration 19 adds semantic dynamic Word fields separate from template placeholders and document metadata.

## Three mechanisms

| Mechanism | Example | Behavior |
|-----------|---------|----------|
| Static placeholder | `{{title}}` | Replaced with static text during template merge |
| Document property | `dc:title` in `docProps/core.xml` | Package metadata |
| Dynamic field | `PAGE`, `TITLE`, `REF` | Word recalculates when the document opens |

`DocumentContext.title` can feed `{{title}}`, `dc:title`, and a `TITLE` field, but they are not the same mechanism. All three read from the same resolved metadata value — see [`DOCUMENT_METADATA.md`](DOCUMENT_METADATA.md).

`DocumentContext.date` is static metadata for template placeholders only. The Word `DATE` field is dynamic and independent.

## Supported fields

| Field | Status | OOXML form |
|-------|--------|------------|
| `PAGE` | supported | `w:fldSimple` |
| `NUMPAGES` | supported | `w:fldSimple` |
| `DATE` | supported | `w:fldSimple` |
| `AUTHOR` | supported | `w:fldSimple` |
| `TITLE` | supported | `w:fldSimple` |
| `REF` | supported | complex field (`\h` headings; `\r \h` figure/table captions) |
| `SEQ` | supported in captions | complex field via `CaptionService` (internal API; Markdown DSL deferred) |
| `TOC` | supported | complex field (heading levels `\o "min-max"`) |
| List of Figures | supported | complex field (`TOC \h \z \c "Figure"`) — programmatic AST only |
| List of Tables | supported | complex field (`TOC \h \z \c "Table"`) — programmatic AST only |

## Markdown directives

```markdown
<!-- footer: page-numbers -->
<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- field: date -->
<!-- field: ref architecture -->
<!-- field: seq Figure -->
<!-- toc -->
```

These use the existing header/footer pipeline and emit real Word fields.

## Architecture

```text
DynamicField
    ↓
FieldManager
    ↓
FieldRenderer
    ↓
md2docx.ooxml.api
    ↓
document.xml / header/footer parts
```

Handlers must not emit raw `w:fldSimple`, `w:fldChar`, or `w:instrText`.

## Settings

When a document contains dynamic fields, the writer emits `word/settings.xml` with:

```xml
<w:updateFields w:val="true"/>
```

CLI:

```bash
md2docx input.md --update-fields
md2docx input.md --no-update-fields
```

Default: update fields on open when the document contains dynamic fields.

## Runtime evaluation

Dynamic fields are generated for WordprocessingML. Their displayed result is recalculated by Microsoft Word or LibreOffice when the document opens or fields are updated. The CLI does not evaluate field results.

See also [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md) for static template placeholders and [`FIGURES_AND_REFERENCES.md`](FIGURES_AND_REFERENCES.md) for figure/table captions using SEQ and REF. See [`NAVIGATION.md`](NAVIGATION.md) for List of Figures/Tables and navigation registry.
