# Advanced Markdown

Iteration 24 adds footnotes, definition lists, and safe inline HTML on top of the existing AST → handler → OOXML pipeline.

## Footnotes

Pandoc-style footnotes:

```markdown
Text with a reference.[^label]

[^label]: Footnote body text.
```

- References become inline `FootnoteReference` AST nodes.
- Definitions are collected on `Document.footnotes` and validated after parsing.
- OOXML uses `word/footnotes.xml`, `w:footnoteReference`, and a footnotes relationship.
- Template merge remaps generated footnote IDs when the template already contains footnotes.

Errors:

```text
Error in README.md: undefined footnote: architecture
Error in README.md: duplicate footnote definition: note
```

## Definition lists

Pandoc/GFM-style definition lists:

```markdown
Term
: Definition paragraph.
```

Rendered as styled paragraphs:

- term — bold Normal paragraph
- description — indented Normal paragraph

There is no native Word definition-list construct.

## Safe inline HTML

Inline HTML tokenization is enabled, but only an allowlisted subset maps to existing AST nodes:

| HTML | AST |
|------|-----|
| `strong`, `b` | `Strong` |
| `em`, `i` | `Emphasis` |
| `del`, `s` | `Strikethrough` |
| `br` | `LineBreak` |
| `a` with safe `href` | `Link` |
| `span` (no attributes) | unwrap children |

Allowed URL schemes: `http`, `https`, `mailto`.

Blocked examples: `script`, `iframe`, `img`, block tags such as `div`.

Unknown inline tags that are not blocked are preserved as literal text so existing escaping fixtures keep working.

Errors:

```text
Error in README.md: unsupported HTML element: iframe
Error in README.md: unsafe URL scheme: javascript
```

## Architecture

| Component | Must not know |
|-----------|---------------|
| `MarkdownParser` / `html_adapter` | OOXML, relationships |
| `FootnoteManager` | Markdown syntax |
| `DefinitionListHandler` | Parser tokens |
| `build_footnotes_xml` | CLI, front matter |

## Parser plugins

```python
MarkdownIt("commonmark", {"html": True})
    .enable("table")
    .enable("strikethrough")
    .use(footnote_plugin, inline=True, move_to_end=True)
    .use(deflist_plugin)
```

HTML comment block directives (`<!-- toc -->`, table directives, etc.) continue to work; HTML comment blocks are skipped during block conversion.
