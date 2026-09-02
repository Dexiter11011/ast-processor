# External Document Themes (YAML)

Iteration 16 adds external YAML themes and the `--theme` CLI flag.

## Architecture

```text
YAML file
    ↓
ThemeLoader (safe_load + schema validation)
    ↓
DocumentTheme (YamlDocumentTheme)
    ↓
ThemeResolver
    ↓
StyleRegistry
    ↓
StylesXmlWriter
    ↓
word/styles.xml
```

YAML never writes OOXML directly. There is no `raw_ooxml`, `xml`, or arbitrary style map in the schema.

## Usage

```bash
md2docx README.md --theme examples/themes/corporate.yaml -o README.docx
```

Without `--theme`, the converter uses `DefaultTheme` exactly as before.

## YAML schema (token-native)

External themes map to [`ThemeTokens`](../src/md2docx/styles/tokens.py) groups. Partial files merge on top of `DefaultTheme`.

### Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | no | Metadata label (default: `unnamed`) |
| `typography` | no | Body, heading, and code fonts/sizes |
| `colors` | no | Text, heading, link, code, quote colors |
| `spacing` | no | Paragraph, heading, list, TOC spacing |
| `headings` | no | Heading level font sizes |
| `page` | no | Page size, orientation, margins |
| `link` | no | Hyperlink presentation |
| `table` | no | Table border/header defaults |

Unknown keys at any level are rejected.

### Typography

```yaml
typography:
  body:
    family: Arial
    size: 11pt
  heading:
    family: Arial
  code:
    family: Consolas
    size: 10pt
```

### Colors

Six-digit hex, with or without `#`:

```yaml
colors:
  text: "222222"
  heading: "123456"
  link: "0563C1"
  code: "333333"
  quote: "666666"
```

### Spacing and headings

```yaml
spacing:
  paragraph_after: 6pt
  heading1_before: 12pt
  list_indent: 0.25in

headings:
  heading1: 28pt
  heading2: 20pt
  heading3: 16pt
```

Supported length units: `pt` (default for bare numbers in spacing), `in`, `cm`, `mm`, `twips`.

Font sizes must use `pt` (or bare numbers interpreted as points).

### Page defaults

```yaml
page:
  size: A4          # or Letter, or {width: 21cm, height: 29.7cm}
  orientation: portrait
  emit_margins: true
  margins:
    top: 2cm
    right: 2cm
    bottom: 2cm
    left: 2cm
```

Explicit section directives override theme page defaults.

## What each token group affects

| Token group | Semantic styles / output |
|-------------|--------------------------|
| `typography` | Normal defaults, headings, code block, inline code |
| `colors` | Body text, heading runs, links, code, quotes |
| `spacing` | Normal, headings, lists, TOC levels |
| `headings` | Heading1/2/3 run sizes |
| `page` | Default section layout |
| `link` | Hyperlink underline |
| `table` | Table border/header presentation |

## Merge semantics

External themes are **partial overrides** on `DefaultTheme`:

1. Start from built-in default tokens.
2. For each YAML group present, merge field-by-field into that group.
3. Pass merged tokens to `ThemeResolver`.

Example minimal theme:

```yaml
name: minimal
colors:
  heading: "111111"
```

All other properties remain from `DefaultTheme`.

## Theme ≠ other systems

| System | Relationship |
|--------|--------------|
| `RenderContext` | Inline bold/italic/strike/code — unchanged by theme file |
| `NumberingManager` | List numId/ilvl — not configured by theme |
| Table layout | Grid/widths — not configured by theme |
| Sections | Explicit section layout beats theme page defaults |

## Validation and errors

- Missing file: `Error: theme file not found: path.yaml`
- Invalid YAML: `Error: invalid theme YAML: line N, column M`
- Schema: `Error: invalid theme: colors.heading must be a 6-digit hex color`
- Unknown key: `Error: invalid theme: typographi unknown theme field`

YAML is loaded with `yaml.safe_load` only.

## Unsupported in this iteration

- JSON theme files
- DOCX template themes
- Theme inheritance / discovery by name
- Per-style YAML maps (`styles.heading1.run.bold`)
- Raw OOXML injection
- `caption`, `table_header`, `table_cell` semantic styles (not in registry)
- Per-heading colors (all headings share `colors.heading`)

## Examples

- [`examples/themes/corporate.yaml`](../examples/themes/corporate.yaml) — full corporate preset
- [`tests/fixtures/themes/minimal.yaml`](../tests/fixtures/themes/minimal.yaml) — single color override

See also [`THEMES.md`](THEMES.md) for the internal theme architecture.
