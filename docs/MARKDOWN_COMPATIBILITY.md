# Совместимость с Markdown

Граница между **возможностями парсера markdown-it** и **возможностями рендеринга md2docx**.

## Поддерживается

| Функция | Markdown | Примечания |
|---------|----------|------------|
| Headings | `#`–`###` | Стили заголовков + закладки |
| Paragraphs | plain text | |
| Bold / italic | `**`, `*`, nested | RenderContext |
| Strikethrough | `~~text~~` | `w:strike` через RenderContext |
| Inline code | `` ` `` | Стиль символов Code |
| Fenced code | ` ``` ` | Стиль NoSpacing |
| Links | `[text](url)` | Внешняя rel или внутренний якорь |
| Autolinks | `<https://...>` | Тот же pipeline Link |
| Reference links | `[t][id]` + `[id]: url` | Тот же pipeline Link |
| Images | `![alt](path)` | |
| Bullet / ordered lists | `-`, `1.` | Numbering.xml |
| Task lists | `- [ ]`, `- [x]` | Префикс символом checkbox (не элементы управления Word) |
| Nested lists | indent | |
| Blockquote | `>` | |
| Horizontal rule | `---` | |
| GFM tables | `\|...\|` | TableGrid, merges, directives |
| Hard line break | two spaces + newline, `\` | `w:br` внутри абзаца |
| Footnotes | `[^label]`, `[^label]: body` | `footnotes.xml`, `w:footnoteReference` |
| Definition lists | `Term` + `: Definition` | стилизованные абзацы |
| Safe inline HTML | `<strong>`, `<em>`, `<del>`, `<br>`, `<a href="https://...">` | сопоставлены с существующими узлами AST |
| Escaped punctuation | `\*`, `\#`, etc. | Правило escape парсера |
| Unicode | any UTF-8 | |
| YAML front matter | `---` header | docProps |
| TOC | `<!-- toc -->`, `<!-- toc: 2-3 -->` | Поле TOC Word |
| List of figures | `<!-- lof -->` | Word `TOC \c "Figure"` |
| List of tables | `<!-- lot -->` | Word `TOC \c "Table"` |
| Figure caption | `![alt](path)` + `<!-- caption: figure ... -->` | SEQ + bookmark |
| Table caption | `<!-- caption: table ... -->` + GFM table | SEQ + bookmark |
| Figure/table ref | `<!-- ref: figure slug -->`, `<!-- ref: table slug -->` | Поле REF |
| Heading ref | `[text](#slug)`, `<!-- field: ref slug -->` | hyperlink / REF |
| Page/section breaks | HTML comment directives | |

См. [`MARKDOWN_NAVIGATION_DSL.md`](MARKDOWN_NAVIGATION_DSL.md) для синтаксиса подписей и перекрёстных ссылок.
См. [`ADVANCED_MARKDOWN.md`](ADVANCED_MARKDOWN.md) для сносок, списков определений и безопасного HTML.

## Частично поддерживается

| Функция | Поведение |
|---------|-----------|
| Текст подписи навигации | Простая строка в HTML-комментарии — без rich inline markdown |
| Только отдельные изображения | Inline `![...](...)` внутри абзаца не объединяется в `Figure` |

| Функция | Поведение |
|---------|-----------|
| Soft break (один `\n` в абзаце) | AST `Text("\n")` — не `w:br`; inline newline CommonMark |

## Не поддерживается

| Функция | Причина |
|---------|---------|
| Bare URL autolink (`https://...` without `<>`) | расширение linkify отключено |
| Unsafe / block HTML | `<script>`, `<div>`, ссылки `javascript:` отклоняются |
| Inline footnotes `^[text]` | необязательно; не покрыто текущими тестами |
| Word interactive checkboxes | элементы task list используют символы Unicode |
| Math, diagrams | вне области |

## Архитектура

```text
Markdown syntax → Parser → AST → Handler → OOXML API → DOCX
```

GFM-функции не должны обходить этот стек. Парсинг Markdown в обработчиках или слое OOXML не выполняется.

## Конфигурация парсера

```python
MarkdownIt("commonmark", {"html": True})
    .enable("table")
    .enable("strikethrough")
    .use(footnote_plugin, inline=True, move_to_end=True)
    .use(deflist_plugin)
```

Состояние task list определяется в постобработке узлов `ListItem` (у markdown-it-py нет правила task-list).
