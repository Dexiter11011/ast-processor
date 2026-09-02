# References and Table of Contents

Iteration 12 separates four related but distinct document navigation mechanisms.

## Four mechanisms

```text
Hyperlink     → jump to URL or in-document anchor
Bookmark      → named anchor inside the document
Cross-reference → pointer to an existing bookmark (internal links cover the primary case)
TOC           → Word field that builds a navigable outline on open
```

These must not be collapsed into one implementation.

## External hyperlinks

Markdown:

```markdown
[OpenAI](https://openai.com)
```

Flow:

```text
Link AST
  → LinkHandler
  → RelationshipManager.add_external_hyperlink(url)
  → api.hyperlink(runs, rel_id=...)
  → w:hyperlink r:id="rIdN"
```

Same URL targets reuse one relationship ID.

## Internal hyperlinks

Markdown:

```markdown
# Introduction

See [the intro](#introduction).
```

Flow:

```text
Heading AST
  → BookmarkManager (pre-scan slugs)
  → HeadingHandler
  → api.heading(..., bookmark_name, bookmark_id)
  → w:bookmarkStart / w:bookmarkEnd

Link AST (#introduction)
  → LinkHandler
  → BookmarkManager.resolve("introduction")
  → api.hyperlink(runs, anchor="introduction")
  → w:hyperlink w:anchor="introduction"   (no relationship)
```

Internal links never create external relationships.

## Heading bookmarks (default-on)

Every heading receives a deterministic bookmark slug derived from its plain text:

| Heading text   | Bookmark name   |
|----------------|-----------------|
| Hello World    | hello-world     |
| API Reference! | api-reference   |
| Introduction (×3) | introduction, introduction-1, introduction-2 |

Slug rules (`references/slug.py`):

- Lowercase, NFKD normalize, punctuation → hyphens
- Unicode letters/digits preserved after normalization
- Empty slug → `section`
- Duplicate slugs get numeric suffixes

Formatting inside headings is ignored for slug text (GitHub-style).

## Broken internal links

```markdown
[Missing](#does-not-exist)
```

When the bookmark is not registered:

- No hyperlink is emitted
- Link text renders as plain inline runs
- Package validation can flag unresolved anchors if they were emitted

Missing bookmarks are never created silently.

## Table of contents

Insert via HTML comment directive (same pattern as page/section breaks):

```markdown
<!-- toc -->
<!-- toc: 2-3 -->
```

Produces a Word complex field:

```text
w:fldChar begin → w:instrText TOC \o "1-3" \h \z \u → w:fldChar separate → w:fldChar end
```

Word updates the visible TOC when the document is opened. The generator does not render a static numbered list.

TOC styles `TOC1`, `TOC2`, `TOC3` are registered in the Style System.

## Ownership

| Concern | Owner |
|---------|-------|
| External URL relationships | `RelationshipManager` |
| Bookmark IDs and slug registry | `BookmarkManager` |
| TOC field instruction | `TocManager` |
| OOXML emission | `md2docx.ooxml.api` |

Handlers must not write raw `w:hyperlink`, `w:bookmarkStart`, `w:bookmarkEnd`, or field XML.

## Components

```text
src/md2docx/references/   Bookmark, BookmarkManager, slug, validator
src/md2docx/toc/          TocSpec, TocManager
src/md2docx/ooxml/bookmark.py
src/md2docx/ooxml/field.py
src/md2docx/elements/toc.py
```

## Tests

- `tests/references/` — slug and BookmarkManager unit tests
- `tests/ooxml/test_bookmark.py`, `test_toc_field.py`
- `tests/integration/test_hyperlinks_docx.py`, `test_bookmarks_docx.py`, `test_toc_docx.py`
- Golden fixtures: `external-links`, `internal-links`, `bookmarks`, `toc`, `references-integration`, …
