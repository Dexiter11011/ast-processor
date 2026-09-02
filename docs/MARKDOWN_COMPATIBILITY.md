# Markdown Compatibility

Boundary between **markdown-it parser capability** and **md2docx rendering capability**.

## Supported

| Feature | Markdown | Notes |
|---------|----------|-------|
| Headings | `#`–`###` | Heading styles + bookmarks |
| Paragraphs | plain text | |
| Bold / italic | `**`, `*`, nested | RenderContext |
| Strikethrough | `~~text~~` | `w:strike` via RenderContext |
| Inline code | `` ` `` | Code character style |
| Fenced code | ` ``` ` | NoSpacing style |
| Links | `[text](url)` | External rel or internal anchor |
| Autolinks | `<https://...>` | Same Link pipeline |
| Reference links | `[t][id]` + `[id]: url` | Same Link pipeline |
| Images | `![alt](path)` | |
| Bullet / ordered lists | `-`, `1.` | Numbering.xml |
| Task lists | `- [ ]`, `- [x]` | Checkbox glyph prefix (not Word controls) |
| Nested lists | indent | |
| Blockquote | `>` | |
| Horizontal rule | `---` | |
| GFM tables | `\|...\|` | TableGrid, merges, directives |
| Hard line break | two spaces + newline, `\` | `w:br` inside paragraph |
| Footnotes | `[^label]`, `[^label]: body` | `footnotes.xml`, `w:footnoteReference` |
| Definition lists | `Term` + `: Definition` | styled paragraphs |
| Safe inline HTML | `<strong>`, `<em>`, `<del>`, `<br>`, `<a href="https://...">` | mapped to existing AST nodes |
| Escaped punctuation | `\*`, `\#`, etc. | Parser escape rule |
| Unicode | any UTF-8 | |
| YAML front matter | `---` header | docProps |
| TOC | `<!-- toc -->`, `<!-- toc: 2-3 -->` | Word TOC field |
| List of figures | `<!-- lof -->` | Word `TOC \c "Figure"` |
| List of tables | `<!-- lot -->` | Word `TOC \c "Table"` |
| Figure caption | `![alt](path)` + `<!-- caption: figure ... -->` | SEQ + bookmark |
| Table caption | `<!-- caption: table ... -->` + GFM table | SEQ + bookmark |
| Figure/table ref | `<!-- ref: figure slug -->`, `<!-- ref: table slug -->` | REF field |
| Heading ref | `[text](#slug)`, `<!-- field: ref slug -->` | hyperlink / REF |
| Page/section breaks | HTML comment directives | |

See [`MARKDOWN_NAVIGATION_DSL.md`](MARKDOWN_NAVIGATION_DSL.md) for caption and cross-reference syntax.
See [`ADVANCED_MARKDOWN.md`](ADVANCED_MARKDOWN.md) for footnotes, definition lists, and safe HTML.

## Partially supported

| Feature | Behavior |
|---------|----------|
| Navigation caption text | Plain string in HTML comment — no rich inline markdown |
| Standalone images only | Inline `![...](...)` inside a paragraph is not coalesced into `Figure` |

| Feature | Behavior |
|---------|----------|
| Soft break (single `\n` in paragraph) | AST `Text("\n")` — not `w:br`; CommonMark inline newline |

## Not supported

| Feature | Reason |
|---------|--------|
| Bare URL autolink (`https://...` without `<>`) | linkify extension disabled |
| Unsafe / block HTML | `<script>`, `<div>`, `javascript:` links rejected |
| Inline footnotes `^[text]` | optional; not covered by current tests |
| Word interactive checkboxes | task items use Unicode glyphs |
| Math, diagrams | out of scope |

## Architecture

```text
Markdown syntax → Parser → AST → Handler → OOXML API → DOCX
```

GFM features must not bypass this stack. No Markdown parsing in handlers or OOXML layer.

## Parser configuration

```python
MarkdownIt("commonmark", {"html": True})
    .enable("table")
    .enable("strikethrough")
    .use(footnote_plugin, inline=True, move_to_end=True)
    .use(deflist_plugin)
```

Task list state is detected in a post-processing pass on `ListItem` nodes (markdown-it-py has no task-list rule).
