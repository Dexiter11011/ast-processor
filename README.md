# md2docx

Standalone CLI that converts Markdown to DOCX through an explicit **AST → OOXML** pipeline.

The tool builds a real Office Open XML package — `document.xml`, `styles.xml`, `numbering.xml`, relationships, media, and `[Content_Types].xml` — without delegating document generation to a black-box DOCX library.

This project is **independent** from `document-platform-ver2`. It lives in the same git repository but has no Python import dependencies on the platform.

## What it does

1. Reads a Markdown file (optional YAML front matter for metadata).
2. Parses Markdown into a typed **AST** (Abstract Syntax Tree).
3. Walks the AST with a single **AstProcessor**, dispatching each node to a dedicated **element handler**.
4. Handlers call the **OOXML layer** to build WordprocessingML elements.
5. Assembles a valid **DOCX** (ZIP archive with XML parts and media).

Supported elements include paragraphs, headings, bold/italic, inline code, links, lists, blockquotes, horizontal rules, code blocks, images, and tables (with formatting directives).

## Install

```bash
cd ast-processor
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Requires **Python 3.9+**.

## Run

```bash
md2docx input.md                  # writes input.docx next to the source file
md2docx input.md -o output.docx   # explicit output path
md2docx input.md -o output.docx --validate   # convert and validate OOXML package
md2docx README.md \
  --title "Final Documentation" \
  --author "John Doe" \
  --date 2026-08-31 \
  -o README.docx                  # CLI overrides YAML front matter (per field)
md2docx --help
md2docx --version
```

Document metadata (title, author, date, subject, keywords) resolves from CLI and YAML front matter into a single model used by template placeholders, core properties, and dynamic fields. See [`docs/DOCUMENT_METADATA.md`](docs/DOCUMENT_METADATA.md).

Errors are printed to stderr (see [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md)):

```text
Error: input file does not exist: document.md
Error: unsupported AST node: footnote
```

Use `--debug` for a full traceback on unexpected internal errors. With `--validate`, invalid output is detected before the final file is replaced, so an existing output file is preserved on validation failure.

## Architecture

Layers are strictly separated. Each layer has one job and must not leak concerns into adjacent layers.

```text
┌─────────────────────────────────────────────────────────────┐
│  CLI (cli/)           argument parsing, exit codes          │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Parser (parser/)     Markdown → AST                        │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  AST (ast/)           typed node definitions                │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Processor (processor/)                                       │
│    AstProcessor       single tree walk, handler dispatch      │
│    HandlerRegistry    type → handler map                      │
│    ProcessingContext  shared document, rels, styles, media    │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Elements (elements/)  one handler per Markdown element       │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  OOXML (ooxml/)       WordprocessingML builders + API         │
│    api.py             facade used by handlers                 │
│    xml_builder.py     safe lxml serialization                 │
│    package.py         DOCX ZIP assembly (lowest OOXML layer)  │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| CLI | `src/md2docx/cli/` | User interface, error messages |
| Parser | `src/md2docx/parser/` | Markdown → AST (no OOXML) |
| AST | `src/md2docx/ast/` | Typed node dataclasses |
| Processor | `src/md2docx/processor/` | AST walk, registry, shared context |
| Elements | `src/md2docx/elements/` | One handler per element type |
| OOXML | `src/md2docx/ooxml/` | XML generation, DOCX package |

**Rule:** Markdown, AST, Processing, OOXML, and ZIP must not be mixed in the same module.

## What is the AST?

The AST is a tree of plain Python dataclasses in `src/md2docx/ast/types.py`. Each node has a `type` string discriminator and fields specific to that construct.

Example — Markdown `Hello **world**` becomes:

```text
Document
└── Paragraph
    ├── Text("Hello ")
    └── Strong
        └── Text("world")
```

Block nodes (`Paragraph`, `Heading`, `List`, `Table`, …) sit at document level. Inline nodes (`Text`, `Strong`, `Link`, …) live inside block nodes. The parser produces the AST; handlers consume it. The AST knows nothing about OOXML or Word.

## How AST becomes OOXML

End-to-end flow (`pipeline.py`):

```text
Markdown file
    → MarkdownParser.parse()          # parser layer
    → Document AST
    → ProcessingContext.create_default()
    → AstProcessor(registry).process_document(ast, context)
         for each node:
           handler = registry.get(node.type)
           handler.process(node, context, processor)
    → OoxmlDocument (accumulated w:p, w:tbl, … in memory)
    → DocxPackageWriter.write_from_context()   # ZIP + all XML parts
    → output.docx
```

**AstProcessor** is a thin dispatcher — it never builds XML itself:

```python
handler = registry.get(node.type)   # raises UnsupportedNodeError if missing
handler.process(node, context, processor)
```

Handlers produce OOXML through two paths:

- **Inline content** — append runs to `context.run_collector`, then a parent handler (e.g. `ParagraphHandler`) flushes them into a paragraph.
- **Block content** — call `context.document.add_*()` helpers that append body-level elements.

All XML is built via **lxml** through `ooxml/xml_builder.py`. User text is never concatenated into tag strings; the serializer handles escaping.

After processing, `DocxPackageWriter` wraps the body in `word/document.xml`, adds `styles.xml`, optional `numbering.xml`, relationship files, media parts, and `[Content_Types].xml`, then writes the ZIP.

## Rendering context

Inline formatting (bold, italic, inline code) flows through an explicit **RenderContext** instead of post-hoc run mutation.

```text
AST inline node
    → InlineHandler (Strong, Emphasis, …)
    → RenderContext.derive()          # push child formatting state
    → AstProcessor.process_children()
    → TextHandler
    → api.run_from_formatting(text, InlineFormatting)
    → apply_inline_formatting → w:rPr (w:b, w:i, w:rStyle)
```

`ProcessingContext` carries both transient collectors and rendering state:

```text
ProcessingContext
├── document, relationships, styles, numbering, media   (shared infrastructure)
├── run_collector                                       (inline run accumulation)
└── render_context: RenderContext
      └── formatting: InlineFormatting { bold, italic, code }
```

**Example trace** — Markdown `**bold *italic***`:

```text
StrongHandler   → derive(bold=True)
  EmphasisHandler → derive(bold=True, italic=True)
    TextHandler   → run_from_formatting("italic", bold=True, italic=True)
```

Hyperlink relationship IDs stay in `RelationshipManager` — never in `InlineFormatting`.

See [`docs/RENDERING_CONTEXT.md`](docs/RENDERING_CONTEXT.md) for the full architecture note.

## Style system

Document-level presentation (headings, quotes, code blocks, lists) flows through a **StyleRegistry** backed by immutable **StyleDefinition** objects.

```text
AST block node
    → Handler selects semantic role (heading1, quote, normal, …)
    → StyleManager.to_ooxml(semantic_id)
    → document.xml w:pStyle / w:rStyle
    → StylesXmlWriter(registry) → word/styles.xml
```

**Style System** (paragraph/character styles) and **Render Context** (inline bold/italic/code) are separate:

```text
# **Hello**  →  pStyle=Heading1  +  run bold=true
```

See [`docs/STYLE_SYSTEM.md`](docs/STYLE_SYSTEM.md), [`docs/LISTS_AND_TABLES.md`](docs/LISTS_AND_TABLES.md), and [`docs/SECTIONS_AND_LAYOUT.md`](docs/SECTIONS_AND_LAYOUT.md).

## How to add a new Markdown element

Adding an element is a **local change** across layers. You do **not** rewrite `AstProcessor`.

Below is a complete sketch for footnotes (`[^1]`). Adapt names and OOXML details to your spec.

### Step 1 — AST type (`ast/types.py`)

```python
@dataclass
class Footnote:
    type: Literal["footnote"] = "footnote"
    id: str = ""
    children: list[InlineNode] = field(default_factory=list)
```

Add `Footnote` to the `InlineNode` (or `BlockNode`) union.

### Step 2 — Parser (`parser/markdown_parser.py`)

Extend the markdown-it token walk to emit `Footnote` nodes when the parser encounters footnote syntax. Parser code must not import handlers or OOXML.

### Step 3 — Handler (`elements/footnote.py`)

```python
from md2docx.ast.types import Footnote
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class FootnoteHandler:
    def process(
        self,
        node: Footnote,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        processor.process_children(node, context)
        runs = list(context.run_collector)
        context.run_collector.clear()
        context.run_collector.append(api.footnote_run(runs, footnote_id=node.id))
```

Handlers use **`md2docx.ooxml.api`** only — not low-level builder modules directly.

### Step 4 — OOXML (`ooxml/footnote.py` + `ooxml/api.py`)

Implement WordprocessingML for footnotes in the OOXML layer:

```python
# ooxml/footnote.py — internal builder using xml_builder.element()
def build_footnote_run(children: list[Element], *, footnote_id: str) -> Element:
    ...

# ooxml/api.py — expose to handlers
def footnote_run(runs: list[Element], *, footnote_id: str) -> Element:
    return build_footnote_run(runs, footnote_id=footnote_id)
```

If footnotes need a new package part (`footnotes.xml`), extend `RelationshipManager`, `content_types.py`, and `DocxPackageWriter` — still without touching the processor.

### Step 5 — Register the handler (`elements/__init__.py`)

```python
from md2docx.elements.footnote import FootnoteHandler

def create_default_registry() -> HandlerRegistry:
    return (
        HandlerRegistry()
        # … existing handlers …
        .register("footnote", FootnoteHandler())
    )
```

That is the only wiring change outside your new files. `AstProcessor` stays unchanged.

### Step 6 — Tests

| Kind | Location | Purpose |
|------|----------|---------|
| Parser unit test | `tests/parser/test_footnote_parser.py` | Markdown → AST |
| Handler unit test | `tests/elements/test_footnote.py` | AST → OOXML fragments |
| Golden test | `tests/expected/footnote.document.xml` | Full `document.xml` snapshot |
| Integration test | `tests/integration/test_footnote_docx.py` | End-to-end DOCX |

Regenerate golden files after intentional OOXML changes:

```bash
python scripts/update-golden.py
# or: pytest tests/golden/ --update-golden
```

### Checklist

- [ ] AST dataclass + union update
- [ ] Parser emits the new node type
- [ ] Handler in `elements/<name>.py`
- [ ] OOXML builder + `api.py` facade
- [ ] `registry.register("<type>", …)` in `create_default_registry()`
- [ ] Tests (parser, handler, golden, integration)
- [ ] **Do not** modify `AstProcessor` unless the tree-walk algorithm itself changes

## Plugins

Load trusted Python extensions with `--plugin`:

```bash
md2docx README.md --plugin examples/plugins/notes_plugin.py -o README.docx
```

See [`docs/PLUGINS.md`](docs/PLUGINS.md) and [`docs/PLUGIN_API.md`](docs/PLUGIN_API.md).

Preferred plugin rendering flow:

```text
Directive → Custom AST → Handler → RichDocumentFragment → existing pipeline → DOCX
```

Use `md2docx.semantic` for new plugins. See [`docs/API.md`](docs/API.md#rich-semantic-api).

## API Stability

Public surface is tiered and tested under `tests/contracts/`:

| Tier | Surface | Stability |
|------|---------|-----------|
| A | `md2docx.plugin_api` (`__all__` only) | Stable v1 |
| B | `styles.definition`, `ooxml.api` (legacy), `semantic` | Stable plugin adjuncts |
| C | CLI flags, exit codes, `--plugin` semantics | Behavioral contract |
| D | `convert_markdown_to_docx`, themes, templates, validation | Experimental programmatic API |

See [`docs/API.md`](docs/API.md) for the manifest and compatibility policy. Plugin authors should follow [`docs/PLUGIN_MIGRATION.md`](docs/PLUGIN_MIGRATION.md). Adding or removing Tier A symbols requires updating `tests/contracts/api_manifest.json`.

## Handler registry

No central `switch` — handlers are registered by AST node type string:

```python
registry = HandlerRegistry()
registry.register("paragraph", ParagraphHandler())
registry.register("heading", HeadingHandler())
registry.register("strong", StrongHandler())
processor = AstProcessor(registry)
```

Built-in wiring lives in `elements.create_default_registry()` (composition root).

## ProcessingContext

Every handler receives the same shared context. Handlers must **not** construct their own `RelationshipManager`, `NumberingManager`, etc.

```python
@dataclass
class ProcessingContext:
    document: OoxmlDocument              # accumulating body elements
    relationships: RelationshipManager   # centralized rId / .rels
    styles: StyleManager                 # semantic role → Word style id
    numbering: NumberingManager          # list numId allocation
    media: MediaManager                  # word/media/* parts
    # transient: list_level, run_collector, block_style, …
```

Created once per conversion via `ProcessingContext.create_default(source_dir=…)`.

## OOXML API

Handlers call the high-level facade instead of assembling raw XML:

```python
from md2docx.ooxml import api

context.run_collector.append(api.run(api.text("Hello")))
context.run_collector.append(api.run("bold", bold=True))
context.document.add_heading(runs, style_id="Heading1")
context.document.add_table(table_ast, rows)
```

Low-level modules (`ooxml/paragraph.py`, `run.py`, `text.py`, …) are internal to the OOXML layer.

## DOCX package parts

`DocxPackageWriter` controls every part of the output:

| Part | Builder |
|------|---------|
| `word/document.xml` | `OoxmlDocument` + body wrapper |
| `word/styles.xml` | `ooxml/styles.py` |
| `word/numbering.xml` | `NumberingManager` (when lists present) |
| `word/_rels/document.xml.rels` | `RelationshipManager` |
| `word/media/*` | `MediaManager` |
| `docProps/core.xml` | `core_props.py` (with YAML metadata) |
| `[Content_Types].xml` | `content_types.py` |
| `_rels/.rels` | `RelationshipManager` |

## DOCX validation

Automatic package validator (`md2docx.validation`) checks structural correctness without opening LibreOffice or Word:

```text
Markdown → DOCX → unzip → validate package → validate XML → validate relationships → validate references
```

| Check | Category | What it verifies |
|-------|----------|------------------|
| ZIP integrity | `package` | archive not corrupt, required parts present |
| Well-formed XML | `xml` | every `.xml` / `.rels` part parses |
| UTF-8 | `unicode` | parts decode as UTF-8 |
| Content Types | `content_types` | each ZIP entry covered by `[Content_Types].xml` |
| Relationships | `relationships` | `_rels/.rels` and `document.xml.rels` targets resolve |
| References | `references` | no dangling `r:id` / `r:embed` in `document.xml` |
| Styles | `styles` | `w:pStyle` / `w:rStyle` reference defined styles |
| Numbering | `numbering` | `w:numId` values exist in `numbering.xml` |
| Media | `media` | images have rels, magic bytes match extension |

```bash
python scripts/validate-docx.py out/bold.docx          # validate one file
python scripts/validate-docx.py --fixtures             # convert + validate all fixtures
md2docx tests/fixtures/bold.md -o /tmp/bold.docx --validate
pytest tests/validation/ -q                            # same checks in CI
```

Structural validation catches broken XML, dangling rIds, and missing parts — the usual causes of Word/LibreOffice recovery dialogs. Manual smoke test in Word/LibreOffice is still recommended before release.

## Testing

```bash
pytest -q                                    # full suite (~238 tests)
pytest tests/parser/test_ast_fixtures.py -q  # Markdown → AST snapshots
pytest tests/golden/ -q                      # document.xml golden files
pytest tests/validation/ -q                  # DOCX package validation
pytest tests/architecture/ -q                # layer boundary guards
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py                  # writes out/BENCHMARK.md
```

Test matrix: [`docs/TEST_MATRIX.md`](docs/TEST_MATRIX.md).

Parser AST fixtures live in `tests/fixtures/ast/*.md` + `*.ast.json` (no DOCX involved).

Optional LibreOffice gate: `pytest tests/integration/test_libreoffice_compat.py` (skipped if not installed).

## Supported Markdown

| Construct | Support |
|-----------|---------|
| Paragraphs | yes |
| Headings `#`–`###` | yes |
| **Bold**, *italic*, nested | yes |
| `` `inline code` `` | yes |
| `[links](url)` | yes (external + internal `#anchor`) |
| `<https://...>` autolinks | yes |
| `[text][ref]` reference links | yes |
| `~~strikethrough~~` | yes |
| `- [ ]` / `- [x]` task lists | yes (glyph prefix) |
| Hard line break (`  ` / `\`) | yes |
| `<!-- toc -->` / `<!-- toc: 1-3 -->` | yes |
| `-` / `1.` lists, nested | yes |
| `>` blockquote | yes |
| `---` horizontal rule | yes |
| Fenced code blocks | yes |
| `![alt](path)` images (PNG, JPEG, …) | yes |
| GFM tables + cell directives | yes |
| YAML front matter | yes |

Images must exist under the Markdown file directory (relative paths only; `../` outside the source tree is rejected). Missing images produce `Error: image not found: ...`.

## Known limitations

Not supported in this release:

- Footnotes, definition lists
- Raw HTML blocks and inline HTML
- Bare URL autolink (without `<>`)
- Math (LaTeX), diagrams (Mermaid)
- Comments
- Different first/odd/even page headers
- Custom Word templates / themes

Built-in theme system exists internally (`DefaultTheme`, token-based `ThemeResolver`). External theme files and `--theme` CLI are not yet exposed. See [`docs/THEMES.md`](docs/THEMES.md).

Unsupported AST node types fail with `Error: unsupported AST node: <type>`.

## Word manual validation checklist

After generating a DOCX (especially `integration-article.docx`), open in Microsoft Word:

- [ ] DOCX opens without a repair dialog
- [ ] Headings display with correct levels and styles
- [ ] Ordered and unordered lists render correctly (including nested)
- [ ] Hyperlinks are clickable
- [ ] Images display at reasonable size
- [ ] Tables: headers, borders, alignment, merges
- [ ] Unicode (Cyrillic, CJK, Arabic, emoji) displays correctly
- [ ] Bold / italic / inline code preserved in body and table cells

## Development

```bash
pytest -q                              # unit, integration, golden, architecture, validation tests
python scripts/build-out.py            # tests + build all fixture DOCX → out/
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py
python scripts/update-golden.py        # refresh tests/expected/*.document.xml
md2docx tests/fixtures/bold.md -o /tmp/bold.docx --validate
```

`scripts/build-out.py` writes to `out/`:

- `test-results.txt` — pytest output
- `<name>.docx` — generated archives
- `<name>/` — unzipped DOCX with pretty-printed XML
- `BUILD_RESULTS.md` — summary

There is no separate lint command configured yet; run `pytest -q` after every change.

## Development rules

1. **Iterate** — do not implement all features at once; ship in small iterations.
2. **Plan each iteration** — before coding, state Goal, Files, Tests, Expected result.
3. **Verify** — after each iteration run tests (and lint/build when available).
4. **Do not regress** — existing fixtures and golden tests must keep passing.
5. **Keep it simple** — no abstractions until a second use case appears.
6. **Respect layer boundaries** — Markdown, AST, Processing, OOXML, ZIP stay separate.
7. **One handler per element** — each Markdown construct maps to one handler class.
8. **Single processor** — one `AstProcessor` owns the AST walk.
9. **OOXML in its own layer** — handlers go through `ooxml.api`, not raw XML strings.
10. **DOCX packaging below OOXML** — ZIP assembly only in `ooxml/package.py`.

Architecture boundary tests in `tests/architecture/test_layer_boundaries.py` enforce several of these rules automatically.

## Technology

This implementation uses **Python** (project spec allows any language; Python was chosen for the standalone prototype):

| Concern | Choice |
|---------|--------|
| Language | Python 3.9+ |
| Markdown parser | [markdown-it-py](https://github.com/executablebooks/markdown-it-py) (token stream → AST) |
| XML | [lxml](https://lxml.de/) via `ooxml/xml_builder.py` (no string-template XML) |
| ZIP / DOCX | stdlib `zipfile` |
| Tests | pytest (unit, integration, golden, architecture) |
| CLI | argparse |

We deliberately **do not** use a library that hides OOXML/DOCX generation (python-docx, pandoc, etc.). We own:

- `document.xml`
- `styles.xml`
- `numbering.xml`
- relationships
- media
- `[Content_Types].xml`

If porting to TypeScript, the same layer split applies: markdown-it or similar → AST → handler registry → XML builder (e.g. lxml equivalent) → ZIP library → Vitest/Jest.

## Iteration history

| Iter | Feature |
|------|---------|
| 0 | Scaffold: CLI, AST, processor, OOXML, tests |
| 1 | Empty Markdown → valid DOCX |
| 2 | Plain text paragraphs |
| 3 | Multiple paragraphs |
| 4 | Headings `#`–`###` |
| 5–6 | Bold, italic |
| 7 | Nested inline formatting |
| 8 | Inline code |
| 9 | Links + hyperlinks rels |
| 10–12 | Unordered, ordered, nested lists + numbering.xml |
| 13 | Blockquote |
| 14 | Horizontal rule |
| 15 | Fenced code blocks |
| 16 | XML escaping (safe serialization) |
| 17 | Images + word/media |
| 18–20 | Tables, formatting, merges, cell directives |
| 21 | Nested inline + escaping edge cases |
| 22 | YAML front matter → docProps |
| 23 | Word styles (headings, Quote, Code, NoSpacing) |
| 24 | Layer boundary refactor, StyleManager/MediaManager |
| 25 | HandlerRegistry + OOXML API facade |
| 26 | Safe XML builder (lxml, no f-string XML) |
| 27 | Golden tests (`tests/expected/*.document.xml`) |
| 28 | CLI UX (`--help`, `--version`, clear errors) |
| 29 | DOCX package validator (XML, rels, content types, media) |
| 30 | Production Readiness Audit (238 tests, `--validate`, AST fixtures, image security) |
| 31 | Rendering Context & Inline Formatting Model (RenderContext, centralized OOXML formatting) |
| 32 | Style System & Document Theme Foundation (StyleRegistry, DefaultTheme, StylesXmlWriter) |
| 33 | Lists, Numbering & Table Styles (ListParagraph, numbering separation, TableGrid, tblHeader) |
| 34 | Sections, Page Layout, Headers & Footers (SectionManager, page/section breaks, header/footer parts) |
| 35 | Bookmarks, Internal/External Hyperlinks, TOC fields (BookmarkManager, slug anchors, Word TOC field) |
| 36 | GFM compatibility (task lists, strikethrough, autolinks, hard breaks) |
| 37 | Document Theme System (tokens, ThemeResolver, theme switching) |
| 38 | Dynamic DOCX Fields (PAGE, REF, SEQ, header/footer directives) |
| 39 | Figures, Captions, Sequences & Cross-References (CaptionService, SEQ Figure/Table, REF `\r \h`; internal API) |
| 40 | Advanced Document Navigation (NavigationRegistry, LOF/LOT, template bookmark remapping, typed REF validation) |

## Captions & cross-references (Iteration 20)

- Figure captions: supported via internal AST API (`Figure` + `Caption`)
- Table captions: supported via `TableWithCaption`
- Figure/table cross-references: `CrossReference` with REF `\r \h`
- Automatic numbering: Word `SEQ Figure` / `SEQ Table` fields (not Python counters)
- Markdown caption syntax: **deferred** — see [`docs/FIGURES_AND_REFERENCES.md`](docs/FIGURES_AND_REFERENCES.md)

## Document navigation (Iteration 21)

- `NavigationRegistry` — semantic heading/figure/table targets in document order
- List of Figures / List of Tables — Word `TOC \c` fields (programmatic AST)
- Template bookmark name remapping — collision suffix `-1`; REF/anchor rewrite in generated fragment
- Typed cross-reference validation via `ReferenceManager`
- See [`docs/NAVIGATION.md`](docs/NAVIGATION.md)

## Project layout

```text
ast-processor/
├── src/md2docx/
│   ├── cli/           # md2docx command
│   ├── parser/        # Markdown → AST
│   ├── ast/           # node types
│   ├── processor/     # AstProcessor, registry, context
│   ├── elements/      # handlers (one file per element)
│   ├── ooxml/         # XML builders, API, DOCX writer
│   └── pipeline.py    # wires layers together
├── tests/
│   ├── fixtures/      # sample .md files
│   ├── expected/      # golden document.xml snapshots
│   ├── golden/        # structural XML comparison tests
│   ├── integration/   # end-to-end DOCX tests
│   └── architecture/  # layer boundary guards
└── scripts/
    ├── build-out.py
    └── update-golden.py
```
