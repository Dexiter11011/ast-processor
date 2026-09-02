---
title: Fields & Metadata Demo
author: Ivan Ivanov
subject: Demonstration of Word fields and document metadata
keywords: fields, metadata, PAGE, TITLE, REF, SEQ, TOC, md2docx
---

<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- footer: page-numbers -->

# Fields & Metadata Demo

<!-- toc -->

Этот документ демонстрирует **все поддерживаемые dynamic fields** md2docx и metadata из YAML front matter.

## Metadata (YAML front matter → core properties)

Значения из блока `---` попадают в `docProps/core.xml`.

| Поле | Значение | Описание |
|------|----------|----------|
| `title` | Fields & Metadata Demo | `dc:title` — заголовок документа |
| `author` | Ivan Ivanov | `dc:creator` — автор |
| `subject` | Demonstration of Word fields and document metadata | тема документа |
| `keywords` | fields, metadata, PAGE, TITLE, … | ключевые слова |

CLI: `--title`, `--author`, `--date` (для template placeholders; `date` не пишется в core props).

## Dynamic fields в колонтитулах

| field | Markdown directive | Описание |
|-------|-------------------|----------|
| `TITLE` | `<!-- header: title-field -->` | заголовок из свойств документа |
| `AUTHOR` | `<!-- header: author-field -->` | автор из `dc:creator` |
| `DATE` | `<!-- header: date-field -->` | текущая дата Word (не `--date`) |
| `PAGE` | `<!-- footer: page-numbers -->` | номер страницы |
| `NUMPAGES` | `<!-- footer: page-numbers -->` | всего страниц («Page N of M») |

В header: TITLE, AUTHOR, DATE (три абзаца). В footer: PAGE + NUMPAGES.

## Dynamic fields в теле документа

| field | Markdown directive | Описание |
|-------|-------------------|----------|
| `DATE` | `<!-- field: date -->` | поле DATE в абзаце |
| `REF` | `<!-- field: ref <bookmark> -->` | cross-reference на bookmark |
| `SEQ` | `<!-- field: seq <name> -->` | нумерация последовательности |
| `TOC` | `<!-- toc -->` | оглавление (см. выше) |

<!-- field: date -->

### Ref Target Section

Заголовок выше получает bookmark `ref-target-section`. Поле REF ссылается на него:

<!-- field: ref ref-target-section -->

### Sequence (Figure)

<!-- field: seq Figure -->

Поле SEQ `Figure` — partial: без caption DSL, только нумерация.

## Template placeholders (только с `--template`)

Статическая подстановка в `.docx` шаблоне — отдельный механизм:

| placeholder | Описание |
|-------------|----------|
| `{{content}}` | тело Markdown |
| `{{title}}` | статический title |
| `{{author}}` | статический author |
| `{{date}}` | явная дата (не system clock) |

```bash
md2docx README.md \
  --template placeholders.docx \
  --title "Project Documentation" \
  --author "John Doe" \
  --date "2026-08-31" \
  -o output.docx
```

## Обычный Markdown

Абзац с **жирным** и *курсивом*. Список:

- пункт 1;
- пункт 2.

Откройте `.docx` в Word и обновите поля — в header/footer и body должны отобразиться все dynamic fields.
