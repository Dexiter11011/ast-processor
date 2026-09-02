# Расширенный Markdown

Итерация 24 добавляет сноски, списки определений и безопасный inline HTML поверх существующего pipeline AST → handler → OOXML.

## Сноски

Сноски в стиле Pandoc:

```markdown
Text with a reference.[^label]

[^label]: Footnote body text.
```

- Ссылки превращаются в inline-узлы AST `FootnoteReference`.
- Определения собираются в `Document.footnotes` и проверяются после парсинга.
- OOXML использует `word/footnotes.xml`, `w:footnoteReference` и связь footnotes.
- При слиянии шаблона ID сгенерированных сносок переназначаются, если в шаблоне уже есть сноски.

Ошибки:

```text
Error in README.md: undefined footnote: architecture
Error in README.md: duplicate footnote definition: note
```

## Списки определений

Списки определений в стиле Pandoc/GFM:

```markdown
Term
: Definition paragraph.
```

Рендерятся как стилизованные абзацы:

- term — абзац Normal жирным
- description — абзац Normal с отступом

В Word нет нативной конструкции списка определений.

## Безопасный inline HTML

Токенизация inline HTML включена, но только разрешённое подмножество сопоставляется с существующими узлами AST:

| HTML | AST |
|------|-----|
| `strong`, `b` | `Strong` |
| `em`, `i` | `Emphasis` |
| `del`, `s` | `Strikethrough` |
| `br` | `LineBreak` |
| `a` with safe `href` | `Link` |
| `span` (no attributes) | unwrap children |

Разрешённые схемы URL: `http`, `https`, `mailto`.

Заблокированные примеры: `script`, `iframe`, `img`, блочные теги вроде `div`.

Неизвестные inline-теги, которые не заблокированы, сохраняются как буквальный текст, чтобы существующие фикстуры escape продолжали работать.

Ошибки:

```text
Error in README.md: unsupported HTML element: iframe
Error in README.md: unsafe URL scheme: javascript
```

## Архитектура

| Компонент | Не должен знать |
|-----------|-----------------|
| `MarkdownParser` / `html_adapter` | OOXML, relationships |
| `FootnoteManager` | Синтаксис Markdown |
| `DefinitionListHandler` | Токены парсера |
| `build_footnotes_xml` | CLI, front matter |

## Плагины парсера

```python
MarkdownIt("commonmark", {"html": True})
    .enable("table")
    .enable("strikethrough")
    .use(footnote_plugin, inline=True, move_to_end=True)
    .use(deflist_plugin)
```

Блочные HTML-комментарии-директивы (`<!-- toc -->`, директивы таблиц и т.д.) продолжают работать; блочные HTML-комментарии пропускаются при блочной конвертации.
